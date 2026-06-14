from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.content import UtpContent
from app.schemas.content import UtpContentResponse, UtpContentByCategory

router = APIRouter()


@router.get("/", response_model=list[UtpContentByCategory])
async def get_all_utp_content(db: AsyncSession = Depends(get_db)):
    """
    Devuelve toda la info de la UTP agrupada por categoría.
    Ej: laboratorios, convenios, empleabilidad, etc.
    """
    result = await db.execute(
        select(UtpContent)
        .where(UtpContent.activo == True)
        .order_by(UtpContent.categoria, UtpContent.orden)
    )
    items = result.scalars().all()

    grouped: dict[str, list] = {}
    for item in items:
        if item.categoria not in grouped:
            grouped[item.categoria] = []
        grouped[item.categoria].append(UtpContentResponse.model_validate(item))

    return [
        UtpContentByCategory(categoria=cat, items=items)
        for cat, items in grouped.items()
    ]


@router.get("/{categoria}", response_model=UtpContentByCategory)
async def get_utp_by_category(categoria: str, db: AsyncSession = Depends(get_db)):
    """Contenido de una categoría UTP específica. Ej: /api/utp/laboratorios"""
    result = await db.execute(
        select(UtpContent)
        .where(UtpContent.categoria == categoria, UtpContent.activo == True)
        .order_by(UtpContent.orden)
    )
    items = result.scalars().all()
    return UtpContentByCategory(
        categoria=categoria,
        items=[UtpContentResponse.model_validate(i) for i in items],
    )