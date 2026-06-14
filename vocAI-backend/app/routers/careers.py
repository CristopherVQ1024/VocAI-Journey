from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.career import Career, Faculty
from app.schemas.career import CareerResponse, CareerSummary, FacultyResponse

router = APIRouter()


@router.get("/", response_model=list[CareerSummary])
async def get_careers(
    db: AsyncSession = Depends(get_db),
    facultad: str | None = Query(None, description="Nombre de la facultad"),
    modalidad: str | None = Query(None, description="presencial | semi_presencial | virtual"),
    demanda_laboral: str | None = Query(None, description="alta | media | baja"),
    trabajo_remoto: bool | None = Query(None),
    buscar: str | None = Query(None, description="Búsqueda por nombre"),
):
    """
    Lista todas las carreras activas con filtros opcionales.
    Es el endpoint principal de la sección Carreras.
    """
    query = (
        select(Career)
        .where(Career.activo == True)
        .options(selectinload(Career.faculty))
        .order_by(Career.nombre)
    )

    if modalidad:
        query = query.where(Career.modalidad == modalidad)
    if demanda_laboral:
        query = query.where(Career.demanda_laboral == demanda_laboral)
    if trabajo_remoto is not None:
        query = query.where(Career.trabajo_remoto == trabajo_remoto)
    if buscar:
        query = query.where(Career.nombre.ilike(f"%{buscar}%"))
    if facultad:
        query = query.join(Faculty).where(Faculty.nombre.ilike(f"%{facultad}%"))

    result = await db.execute(query)
    careers = result.scalars().all()
    return careers


@router.get("/faculties", response_model=list[FacultyResponse])
async def get_faculties(db: AsyncSession = Depends(get_db)):
    """Lista todas las facultades. Útil para poblar el filtro del frontend."""
    result = await db.execute(select(Faculty).order_by(Faculty.nombre))
    return result.scalars().all()


@router.get("/{slug}", response_model=CareerResponse)
async def get_career(slug: str, db: AsyncSession = Depends(get_db)):
    """Detalle completo de una carrera por su slug."""
    result = await db.execute(
        select(Career)
        .where(Career.slug == slug, Career.activo == True)
        .options(selectinload(Career.faculty))
    )
    career = result.scalar_one_or_none()
    if not career:
        raise HTTPException(status_code=404, detail="Carrera no encontrada")
    return career