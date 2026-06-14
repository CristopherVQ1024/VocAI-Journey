from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.core.database import get_db
from app.models.career import Career, Faculty
from app.schemas.career import CareerResponse, CareerSummary, FacultyResponse, CareerCreate, CareerUpdate, FacultyCreate, FacultyUpdate

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

@router.get("/id/{career_id}", response_model=CareerResponse)
async def get_career_by_id(
    career_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener carrera por ID.
    """

    result = await db.execute(
        select(Career)
        .where(Career.id == career_id)
        .options(selectinload(Career.faculty))
    )

    career = result.scalar_one_or_none()

    if not career:
        raise HTTPException(
            status_code=404,
            detail="Carrera no encontrada"
        )

    return career

@router.post("/", response_model=CareerResponse)
async def create_career(
    data: CareerCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Crear una carrera nueva.
    """

    # verificar facultad
    faculty_result = await db.execute(
        select(Faculty).where(
            Faculty.id == data.faculty_id
        )
    )

    faculty = faculty_result.scalar_one_or_none()

    if not faculty:
        raise HTTPException(
            status_code=404,
            detail="Facultad no encontrada"
        )

    # verificar slug duplicado
    slug_result = await db.execute(
        select(Career).where(
            Career.slug == data.slug
        )
    )

    career_exists = slug_result.scalar_one_or_none()

    if career_exists:
        raise HTTPException(
            status_code=400,
            detail="Ya existe una carrera con ese slug"
        )

    new_career = Career(
        faculty_id=data.faculty_id,
        nombre=data.nombre,
        slug=data.slug,
        descripcion_corta=data.descripcion_corta,
        duracion_semestres=data.duracion_semestres,
        modalidad=data.modalidad,
        imagen_url=data.imagen_url,
        color_hex=data.color_hex,
        demanda_laboral=data.demanda_laboral,
        trabajo_remoto=data.trabajo_remoto,
        salario_min=data.salario_min,
        salario_promedio=data.salario_promedio,
        salario_max=data.salario_max,
        activo=data.activo,
    )

    db.add(new_career)

    await db.commit()
    await db.refresh(new_career)

    result = await db.execute(
        select(Career)
        .where(Career.id == new_career.id)
        .options(selectinload(Career.faculty))
    )

    return result.scalar_one()

@router.put("/{career_id}", response_model=CareerResponse)
async def update_career(
    career_id: UUID,
    data: CareerUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar carrera.
    """

    result = await db.execute(
        select(Career)
        .where(Career.id == career_id)
        .options(selectinload(Career.faculty))
    )

    career = result.scalar_one_or_none()

    if not career:
        raise HTTPException(
            status_code=404,
            detail="Carrera no encontrada"
        )

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(career, key, value)

    await db.commit()
    await db.refresh(career)

    return career

@router.delete("/{career_id}")
async def delete_career(
    career_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Desactiva una carrera.
    """

    result = await db.execute(
        select(Career).where(
            Career.id == career_id
        )
    )

    career = result.scalar_one_or_none()

    if not career:
        raise HTTPException(
            status_code=404,
            detail="Carrera no encontrada"
        )

    career.activo = False

    await db.commit()

    return {
        "message": "Carrera desactivada"
    }


    # ─── Crear facultad ─────────────────────────────────────────────────────────

@router.post("/faculties", response_model=FacultyResponse, status_code=201)
async def create_faculty(
    data: FacultyCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Crear nueva facultad.
    """
    # Validar duplicado
    result = await db.execute(
        select(Faculty).where(Faculty.nombre.ilike(data.nombre))
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Ya existe una facultad con ese nombre"
        )

    faculty = Faculty(
        nombre=data.nombre,
        descripcion=data.descripcion,
    )

    db.add(faculty)
    await db.commit()
    await db.refresh(faculty)

    return faculty


# ─── Actualizar facultad ────────────────────────────────────────────────────

@router.put("/faculties/{faculty_id}", response_model=FacultyResponse)
async def update_faculty(
    faculty_id: UUID,
    data: FacultyUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Actualizar facultad.
    """
    result = await db.execute(
        select(Faculty).where(Faculty.id == faculty_id)
    )
    faculty = result.scalar_one_or_none()

    if not faculty:
        raise HTTPException(
            status_code=404,
            detail="Facultad no encontrada"
        )

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(faculty, key, value)

    await db.commit()
    await db.refresh(faculty)

    return faculty


# ─── Eliminar facultad ──────────────────────────────────────────────────────

@router.delete("/faculties/{faculty_id}")
async def delete_faculty(
    faculty_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Eliminar facultad.
    """
    result = await db.execute(
        select(Faculty).where(Faculty.id == faculty_id)
    )
    faculty = result.scalar_one_or_none()

    if not faculty:
        raise HTTPException(
            status_code=404,
            detail="Facultad no encontrada"
        )

    # Validar que no tenga carreras
    careers_result = await db.execute(
        select(Career).where(Career.faculty_id == faculty_id)
    )
    careers = careers_result.scalars().all()

    if careers:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar la facultad porque tiene carreras asociadas"
        )

    await db.delete(faculty)
    await db.commit()

    return {
        "message": "Facultad eliminada correctamente"
    }