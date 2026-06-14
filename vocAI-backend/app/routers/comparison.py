from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.session import (
    VocationalSession,
    SessionSelectedCareer,
    SessionSectionAnswer,
)
from app.models.comparison import ComparisonSection, CareerCard
from app.models.career import Career
from app.schemas.session import (
    SessionCreate,
    SessionResponse,
    SelectCareersInput,
    SectionAnswerInput,
    SectionAnswerResponse,
)
from app.schemas.comparison import ComparisonStepResponse, ComparisonSectionResponse, CareerCardResponse

router = APIRouter()


@router.post("/session", response_model=SessionResponse, status_code=201)
async def create_session(
    data: SessionCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Inicia una nueva sesión del journey.
    Funciona sin login usando guest_token generado por el frontend.
    """
    session = VocationalSession(
        guest_token=data.guest_token,
        status="in_progress",
    )
    db.add(session)
    await db.flush()
    return session


@router.post("/session/{session_id}/careers", status_code=201)
async def select_careers(
    session_id: str,
    data: SelectCareersInput,
    db: AsyncSession = Depends(get_db),
):
    """
    El alumno elige las 3 carreras que quiere comparar.
    Máximo 3 — se valida aquí.
    """
    if len(data.career_ids) != 3:
        raise HTTPException(status_code=400, detail="Debes seleccionar exactamente 3 carreras")

    # Verificar que la sesión existe
    result = await db.execute(
        select(VocationalSession).where(VocationalSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    # Guardar las 3 carreras seleccionadas
    for orden, career_id in enumerate(data.career_ids, start=1):
        score = data.compatibility_scores.get(str(career_id), 0.0)
        selected = SessionSelectedCareer(
            session_id=session.id,
            career_id=career_id,
            compatibility_score=score,
            selected_order=orden,
        )
        db.add(selected)

    return {"message": "Carreras seleccionadas correctamente", "session_id": str(session.id)}


@router.get("/session/{session_id}/step/{step_order}", response_model=ComparisonStepResponse)
async def get_step(
    session_id: str,
    step_order: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Devuelve el contenido de un paso del journey.
    step_order va del 1 al 8 según las comparison_sections.
    Incluye las 3 cards (una por carrera seleccionada).
    """
    # Obtener la sección correspondiente al paso
    result = await db.execute(
        select(ComparisonSection)
        .where(ComparisonSection.orden == step_order, ComparisonSection.activo == True)
    )
    section = result.scalar_one_or_none()
    if not section:
        raise HTTPException(status_code=404, detail=f"Paso {step_order} no encontrado")

    # Obtener las carreras seleccionadas en esta sesión
    result = await db.execute(
        select(SessionSelectedCareer)
        .where(SessionSelectedCareer.session_id == session_id)
        .order_by(SessionSelectedCareer.selected_order)
    )
    selected = result.scalars().all()
    if not selected:
        raise HTTPException(status_code=400, detail="No hay carreras seleccionadas para esta sesión")

    career_ids = [s.career_id for s in selected]

    # Obtener las cards de esas carreras para esta sección
    result = await db.execute(
        select(CareerCard)
        .where(
            CareerCard.section_id == section.id,
            CareerCard.career_id.in_(career_ids),
            CareerCard.is_active == True,
        )
    )
    cards = result.scalars().all()

    # Total de secciones activas
    total_result = await db.execute(
        select(ComparisonSection).where(ComparisonSection.activo == True)
    )
    total_steps = len(total_result.scalars().all())

    return ComparisonStepResponse(
        section=ComparisonSectionResponse.model_validate(section),
        cards=[CareerCardResponse.model_validate(c) for c in cards],
        total_steps=total_steps,
        current_step=step_order,
    )


@router.post("/session/{session_id}/answer", response_model=SectionAnswerResponse, status_code=201)
async def submit_answer(
    session_id: str,
    data: SectionAnswerInput,
    db: AsyncSession = Depends(get_db),
):
    """
    Guarda la elección del alumno en un paso.
    'Esta conectó más conmigo' → suma 10 puntos a esa carrera.
    """
    # Verificar que no haya respondido ya esta sección
    result = await db.execute(
        select(SessionSectionAnswer).where(
            SessionSectionAnswer.session_id == session_id,
            SessionSectionAnswer.section_id == data.section_id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Ya respondiste esta sección")

    answer = SessionSectionAnswer(
        session_id=session_id,
        section_id=data.section_id,
        selected_career_id=data.selected_career_id,
        score_awarded=10,
    )
    db.add(answer)
    await db.flush()
    return answer