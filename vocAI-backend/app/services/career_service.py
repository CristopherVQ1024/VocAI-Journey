from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.career import Career, Faculty
from app.schemas.career import CareerFilters


class CareerService:

    @staticmethod
    async def get_all(db: AsyncSession, filters: CareerFilters) -> list[Career]:
        """
        Retorna carreras activas aplicando filtros opcionales.
        Separado del router para poder reutilizarlo (ej: en el journey).
        """
        query = (
            select(Career)
            .where(Career.activo == True)
            .options(selectinload(Career.faculty))
            .order_by(Career.nombre)
        )

        if filters.modalidad:
            query = query.where(Career.modalidad == filters.modalidad)
        if filters.demanda_laboral:
            query = query.where(Career.demanda_laboral == filters.demanda_laboral)
        if filters.trabajo_remoto is not None:
            query = query.where(Career.trabajo_remoto == filters.trabajo_remoto)
        if filters.buscar:
            query = query.where(Career.nombre.ilike(f"%{filters.buscar}%"))
        if filters.facultad:
            query = query.join(Faculty).where(
                Faculty.nombre.ilike(f"%{filters.facultad}%")
            )

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_by_slug(db: AsyncSession, slug: str) -> Career | None:
        """Retorna una carrera por slug o None si no existe."""
        result = await db.execute(
            select(Career)
            .where(Career.slug == slug, Career.activo == True)
            .options(selectinload(Career.faculty))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_ids(db: AsyncSession, ids: list) -> list[Career]:
        """Retorna varias carreras por sus IDs. Útil al iniciar el journey."""
        result = await db.execute(
            select(Career)
            .where(Career.id.in_(ids), Career.activo == True)
            .options(selectinload(Career.faculty))
        )
        return result.scalars().all()