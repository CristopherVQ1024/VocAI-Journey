from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.session import (
    VocationalSession,
    SessionSelectedCareer,
    SessionSectionAnswer,
    SessionRankingResult,
    SavedRanking,
)
from app.models.comparison import ComparisonSection
from app.models.career import Career
from app.schemas.session import (
    FullRankingResponse,
    RankingResultResponse,
    SaveRankingInput,
    SavedRankingResponse,
)
from app.schemas.career import CareerSummary

router = APIRouter()


@router.post("/generate/{session_id}", response_model=FullRankingResponse)
async def generate_ranking(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Genera el ranking final al completar las 8 secciones.
    Fórmula: final_score = (compatibility * 0.4) + (interaction * 0.6)
    Luego llama a la IA para generar la justificación del #1.
    """
    # Verificar sesión
    result = await db.execute(
        select(VocationalSession).where(VocationalSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    # Verificar que completó todas las secciones
    total_sections_result = await db.execute(
        select(func.count()).where(ComparisonSection.activo == True)
    )
    total_sections = total_sections_result.scalar()

    answers_result = await db.execute(
        select(func.count()).where(SessionSectionAnswer.session_id == session_id)
    )
    total_answers = answers_result.scalar()

    if total_answers < total_sections:
        raise HTTPException(
            status_code=400,
            detail=f"Debes completar todas las secciones ({total_answers}/{total_sections})",
        )

    # Obtener carreras seleccionadas con su compatibility_score
    selected_result = await db.execute(
        select(SessionSelectedCareer)
        .where(SessionSelectedCareer.session_id == session_id)
        .options(selectinload(SessionSelectedCareer.career).selectinload(Career.faculty))
    )
    selected_careers = selected_result.scalars().all()

    # Sumar interaction_score por carrera (10 pts por cada sección elegida)
    answers_result = await db.execute(
        select(SessionSectionAnswer)
        .where(SessionSectionAnswer.session_id == session_id)
    )
    answers = answers_result.scalars().all()

    # Agrupar scores de interacción por carrera
    interaction_scores: dict[str, float] = {}
    for answer in answers:
        key = str(answer.selected_career_id)
        interaction_scores[key] = interaction_scores.get(key, 0) + answer.score_awarded

    # Normalizar interaction_score a 100 (máximo = total_sections * 10)
    max_interaction = total_sections * 10

    # Calcular final_score y ordenar
    ranking_data = []
    for sc in selected_careers:
        career_key = str(sc.career_id)
        compatibility = float(sc.compatibility_score)
        interaction_raw = interaction_scores.get(career_key, 0)
        interaction_normalized = (interaction_raw / max_interaction) * 100

        final = (compatibility * 0.4) + (interaction_normalized * 0.6)

        ranking_data.append({
            "career": sc.career,
            "compatibility_score": round(compatibility, 2),
            "interaction_score": round(interaction_normalized, 2),
            "final_score": round(final, 2),
        })

    # Ordenar de mayor a menor final_score
    ranking_data.sort(key=lambda x: x["final_score"], reverse=True)

    # Generar justificación IA para el #1
    winner = ranking_data[0]
    ai_justification = await _generate_justification(winner["career"].nombre, answers, selected_careers)

    # Guardar resultados en BD
    results = []
    for position, item in enumerate(ranking_data, start=1):
        rr = SessionRankingResult(
            session_id=session_id,
            career_id=item["career"].id,
            ranking_position=position,
            compatibility_score=item["compatibility_score"],
            interaction_score=item["interaction_score"],
            final_score=item["final_score"],
            ai_justification=ai_justification if position == 1 else None,
        )
        db.add(rr)
        results.append(rr)

    await db.flush()

    # Marcar sesión como completada
    session.status = "completed"
    from datetime import datetime
    session.completed_at = datetime.utcnow()

    return FullRankingResponse(
        session_id=session.id,
        results=[
            RankingResultResponse(
                ranking_position=position + 1,
                career=CareerSummary.model_validate(item["career"]),
                compatibility_score=item["compatibility_score"],
                interaction_score=item["interaction_score"],
                final_score=item["final_score"],
                ai_justification=ai_justification if position == 0 else None,
            )
            for position, item in enumerate(ranking_data)
        ],
    )


@router.get("/{session_id}", response_model=FullRankingResponse)
async def get_ranking(session_id: str, db: AsyncSession = Depends(get_db)):
    """Recupera el ranking ya generado de una sesión completada."""
    result = await db.execute(
        select(SessionRankingResult)
        .where(SessionRankingResult.session_id == session_id)
        .options(
            selectinload(SessionRankingResult.career).selectinload(Career.faculty)
        )
        .order_by(SessionRankingResult.ranking_position)
    )
    results = result.scalars().all()
    if not results:
        raise HTTPException(status_code=404, detail="Ranking no encontrado")

    return FullRankingResponse(
        session_id=session_id,
        results=[
            RankingResultResponse(
                ranking_position=r.ranking_position,
                career=CareerSummary.model_validate(r.career),
                compatibility_score=float(r.compatibility_score),
                interaction_score=float(r.interaction_score),
                final_score=float(r.final_score),
                ai_justification=r.ai_justification,
            )
            for r in results
        ],
    )


@router.post("/{session_id}/save", response_model=SavedRankingResponse, status_code=201)
async def save_ranking(
    session_id: str,
    data: SaveRankingInput,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Guarda el ranking con un nombre. Solo para usuarios logueados."""
    saved = SavedRanking(
        user_id=user_id,
        session_id=session_id,
        nombre=data.nombre,
    )
    db.add(saved)
    await db.flush()
    return saved


# ─── Función interna para llamar a la IA ────────────────────────────────────

async def _generate_justification(
    career_nombre: str,
    answers: list,
    selected_careers: list,
) -> str:
    """
    Genera una justificación personalizada usando la API de Anthropic.
    Si falla, devuelve un texto genérico para no romper el flujo.
    """
    try:
        import httpx
        from app.core.config import settings

        if not settings.ANTHROPIC_API_KEY:
            return _fallback_justification(career_nombre)

        # Construir contexto de las elecciones del alumno
        career_names = {str(sc.career_id): sc.career.nombre for sc in selected_careers}
        choices_text = "\n".join(
            [f"- Sección {i+1}: eligió {career_names.get(str(a.selected_career_id), 'desconocida')}"
             for i, a in enumerate(answers)]
        )

        prompt = f"""Eres un orientador vocacional amigable. 
El alumno comparó 3 carreras y {career_nombre} quedó en primer lugar.

Sus elecciones sección por sección fueron:
{choices_text}

Escribe UNA sola oración de justificación personalizada, cálida y motivadora.
Máximo 2 líneas. No uses listas. Empieza con '{career_nombre} destacó porque...'"""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-haiku-4-5-20251001",
                    "max_tokens": 150,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=15.0,
            )
            data = response.json()
            return data["content"][0]["text"].strip()

    except Exception:
        return _fallback_justification(career_nombre)


def _fallback_justification(career_nombre: str) -> str:
    return (
        f"{career_nombre} destacó porque fue la carrera con la que más conectaste "
        f"a lo largo de la comparación. ¡Es una excelente señal para tu decisión!"
    )