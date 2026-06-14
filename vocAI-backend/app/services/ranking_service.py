from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.session import (
    SessionSelectedCareer,
    SessionSectionAnswer,
    SessionRankingResult,
)
from app.models.career import Career


class RankingService:

    @staticmethod
    async def calculate(
        db: AsyncSession,
        session_id: str,
        selected_careers: list[SessionSelectedCareer],
        answers: list[SessionSectionAnswer],
        total_sections: int,
    ) -> list[dict]:
        """
        Calcula el ranking final combinando:
        - compatibility_score: viene del test vocacional (peso 40%)
        - interaction_score: elecciones en el journey (peso 60%)

        Retorna lista ordenada de mayor a menor final_score.
        """
        # Sumar puntos de interacción por carrera
        interaction_map: dict[str, float] = {}
        for answer in answers:
            key = str(answer.selected_career_id)
            interaction_map[key] = interaction_map.get(key, 0) + answer.score_awarded

        # Normalizar interaction a 100
        max_interaction = total_sections * 10

        ranking_data = []
        for sc in selected_careers:
            key = str(sc.career_id)
            compatibility = float(sc.compatibility_score)
            interaction_raw = interaction_map.get(key, 0)
            interaction_normalized = (
                (interaction_raw / max_interaction) * 100 if max_interaction > 0 else 0
            )
            final = round((compatibility * 0.4) + (interaction_normalized * 0.6), 2)

            ranking_data.append({
                "career": sc.career,
                "compatibility_score": round(compatibility, 2),
                "interaction_score": round(interaction_normalized, 2),
                "final_score": final,
            })

        # Ordenar de mayor a menor
        ranking_data.sort(key=lambda x: x["final_score"], reverse=True)
        return ranking_data

    @staticmethod
    async def save(
        db: AsyncSession,
        session_id: str,
        ranking_data: list[dict],
        ai_justification: str,
    ) -> list[SessionRankingResult]:
        """Persiste el ranking calculado en la BD."""
        results = []
        for position, item in enumerate(ranking_data, start=1):
            rr = SessionRankingResult(
                session_id=session_id,
                career_id=item["career"].id,
                ranking_position=position,
                compatibility_score=item["compatibility_score"],
                interaction_score=item["interaction_score"],
                final_score=item["final_score"],
                # Solo el #1 recibe la justificación de IA
                ai_justification=ai_justification if position == 1 else None,
            )
            db.add(rr)
            results.append(rr)

        await db.flush()
        return results

    @staticmethod
    async def get_by_session(
        db: AsyncSession, session_id: str
    ) -> list[SessionRankingResult]:
        """Recupera el ranking guardado de una sesión."""
        result = await db.execute(
            select(SessionRankingResult)
            .where(SessionRankingResult.session_id == session_id)
            .options(
                selectinload(SessionRankingResult.career).selectinload(Career.faculty)
            )
            .order_by(SessionRankingResult.ranking_position)
        )
        return result.scalars().all()


class AIService:

    @staticmethod
    async def generate_justification(
        career_nombre: str,
        answers: list[SessionSectionAnswer],
        selected_careers: list[SessionSelectedCareer],
    ) -> str:
        """
        Llama a la API de Anthropic para generar una justificación
        personalizada basada en las elecciones del alumno.
        Si falla por cualquier razón, devuelve un texto genérico
        para no romper el flujo del usuario.
        """
        try:
            import httpx
            from app.core.config import settings

            if not settings.ANTHROPIC_API_KEY:
                return AIService._fallback(career_nombre)

            # Construir contexto de elecciones
            career_names = {
                str(sc.career_id): sc.career.nombre for sc in selected_careers
            }
            choices_text = "\n".join([
                f"- Sección {i + 1}: eligió {career_names.get(str(a.selected_career_id), 'desconocida')}"
                for i, a in enumerate(answers)
            ])

            prompt = f"""Eres un orientador vocacional amigable y motivador.
El alumno comparó 3 carreras universitarias paso a paso y {career_nombre} quedó en primer lugar.

Sus elecciones durante la comparación fueron:
{choices_text}

Escribe UNA justificación personalizada, cálida y motivadora de máximo 2 líneas.
No uses listas ni bullet points. Solo texto corrido.
Empieza con '{career_nombre} destacó porque...'"""

            async with httpx.AsyncClient(timeout=15.0) as client:
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
                )
                data = response.json()
                return data["content"][0]["text"].strip()

        except Exception:
            # Nunca romper el flujo por un error de IA
            return AIService._fallback(career_nombre)

    @staticmethod
    def _fallback(career_nombre: str) -> str:
        return (
            f"{career_nombre} destacó porque fue la carrera con la que más "
            f"conectaste a lo largo de la comparación. "
            f"¡Es una excelente señal para tu decisión vocacional!"
        )