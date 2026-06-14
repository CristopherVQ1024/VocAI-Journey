from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.session import (
    VocationalSession,
    SessionSelectedCareer,
    SessionSectionAnswer,
)
from app.models.career import Career
from app.models.comparison import ComparisonSection


class SessionService:

    @staticmethod
    async def create(db: AsyncSession, guest_token: str | None = None, user_id=None) -> VocationalSession:
        """Crea una nueva sesión de journey."""
        session = VocationalSession(
            user_id=user_id,
            guest_token=guest_token,
            status="in_progress",
        )
        db.add(session)
        await db.flush()
        return session

    @staticmethod
    async def get_by_id(db: AsyncSession, session_id: str) -> VocationalSession:
        """Obtiene una sesión o lanza 404."""
        result = await db.execute(
            select(VocationalSession).where(VocationalSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        return session

    @staticmethod
    async def select_careers(
        db: AsyncSession,
        session_id: str,
        career_ids: list,
        compatibility_scores: dict,
    ) -> list[SessionSelectedCareer]:
        """
        Guarda las 3 carreras elegidas para la sesión.
        Valida que sean exactamente 3 y que no estén ya seleccionadas.
        """
        if len(career_ids) != 3:
            raise HTTPException(
                status_code=400,
                detail="Debes seleccionar exactamente 3 carreras",
            )

        # Verificar que no haya selección previa
        existing = await db.execute(
            select(SessionSelectedCareer).where(
                SessionSelectedCareer.session_id == session_id
            )
        )
        if existing.scalars().first():
            raise HTTPException(
                status_code=400,
                detail="Esta sesión ya tiene carreras seleccionadas",
            )

        selected = []
        for orden, career_id in enumerate(career_ids, start=1):
            score = compatibility_scores.get(str(career_id), 0.0)
            sc = SessionSelectedCareer(
                session_id=session_id,
                career_id=career_id,
                compatibility_score=score,
                selected_order=orden,
            )
            db.add(sc)
            selected.append(sc)

        await db.flush()
        return selected

    @staticmethod
    async def get_selected_careers(
        db: AsyncSession, session_id: str
    ) -> list[SessionSelectedCareer]:
        """Retorna las carreras seleccionadas de una sesión con su info completa."""
        result = await db.execute(
            select(SessionSelectedCareer)
            .where(SessionSelectedCareer.session_id == session_id)
            .options(
                selectinload(SessionSelectedCareer.career).selectinload(Career.faculty)
            )
            .order_by(SessionSelectedCareer.selected_order)
        )
        return result.scalars().all()

    @staticmethod
    async def submit_answer(
        db: AsyncSession,
        session_id: str,
        section_id: str,
        selected_career_id: str,
    ) -> SessionSectionAnswer:
        """
        Guarda la respuesta del alumno en una sección.
        Valida que no haya respondido ya esa sección.
        """
        existing = await db.execute(
            select(SessionSectionAnswer).where(
                SessionSectionAnswer.session_id == session_id,
                SessionSectionAnswer.section_id == section_id,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Ya respondiste esta sección",
            )

        answer = SessionSectionAnswer(
            session_id=session_id,
            section_id=section_id,
            selected_career_id=selected_career_id,
            score_awarded=10,
        )
        db.add(answer)
        await db.flush()
        return answer

    @staticmethod
    async def get_answers(
        db: AsyncSession, session_id: str
    ) -> list[SessionSectionAnswer]:
        """Retorna todas las respuestas de una sesión."""
        result = await db.execute(
            select(SessionSectionAnswer).where(
                SessionSectionAnswer.session_id == session_id
            )
        )
        return result.scalars().all()

    @staticmethod
    async def count_active_sections(db: AsyncSession) -> int:
        """Cuenta el total de secciones activas del journey."""
        result = await db.execute(
            select(func.count()).where(ComparisonSection.activo == True)
        )
        return result.scalar()

    @staticmethod
    async def is_complete(db: AsyncSession, session_id: str) -> bool:
        """Verifica si el alumno respondió todas las secciones."""
        total = await SessionService.count_active_sections(db)
        answers = await SessionService.get_answers(db, session_id)
        return len(answers) >= total

    @staticmethod
    async def mark_completed(db: AsyncSession, session: VocationalSession) -> None:
        """Marca la sesión como completada."""
        from datetime import datetime
        session.status = "completed"
        session.completed_at = datetime.utcnow()