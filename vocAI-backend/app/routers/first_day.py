from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.content import UniversityExperienceContent
from app.schemas.content import ExperienceContentResponse, ExperienceContentByCategory

router = APIRouter()

# Categorías válidas del módulo
CATEGORIAS = ["first_day", "friends", "classes", "teachers", "exams", "campus", "clubs", "tips", "fears"]


@router.get("/", response_model=list[ExperienceContentByCategory])
async def get_all_content(db: AsyncSession = Depends(get_db)):
    """
    Devuelve todo el contenido de 'Mi Primer Día' agrupado por categoría.
    El frontend muestra cada grupo como una subsección.
    """
    result = await db.execute(
        select(UniversityExperienceContent)
        .where(UniversityExperienceContent.is_active == True)
        .order_by(UniversityExperienceContent.categoria, UniversityExperienceContent.orden)
    )
    items = result.scalars().all()

    # Agrupar por categoría
    grouped: dict[str, list] = {}
    for item in items:
        if item.categoria not in grouped:
            grouped[item.categoria] = []
        grouped[item.categoria].append(ExperienceContentResponse.model_validate(item))

    return [
        ExperienceContentByCategory(categoria=cat, items=items)
        for cat, items in grouped.items()
    ]


@router.get("/{categoria}", response_model=ExperienceContentByCategory)
async def get_by_category(
    categoria: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Contenido de una categoría específica.
    Ej: GET /api/first-day/fears → miedos comunes
    """
    result = await db.execute(
        select(UniversityExperienceContent)
        .where(
            UniversityExperienceContent.categoria == categoria,
            UniversityExperienceContent.is_active == True,
        )
        .order_by(UniversityExperienceContent.orden)
    )
    items = result.scalars().all()
    return ExperienceContentByCategory(
        categoria=categoria,
        items=[ExperienceContentResponse.model_validate(i) for i in items],
    )