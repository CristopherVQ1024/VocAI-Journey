from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.comparison import ComparisonSection, CareerCard


class ComparisonSectionService:

    @staticmethod
    async def get_all(db: AsyncSession):
        result = await db.execute(
            select(ComparisonSection)
            .order_by(ComparisonSection.orden)
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, section_id):
        result = await db.execute(
            select(ComparisonSection)
            .where(ComparisonSection.id == section_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_slug(db: AsyncSession, slug: str):
        result = await db.execute(
            select(ComparisonSection)
            .where(ComparisonSection.slug == slug)
        )
        return result.scalar_one_or_none()
    

    # ==========================================================
    # Career Cards
    # ==========================================================

    @staticmethod
    async def get_all_cards(
        db: AsyncSession,
    ) -> list[CareerCard]:
        result = await db.execute(
            select(CareerCard)
            .order_by(CareerCard.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_card_by_id(
        db: AsyncSession,
        card_id,
    ) -> CareerCard | None:
        result = await db.execute(
            select(CareerCard)
            .where(CareerCard.id == card_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_card_by_career_and_section(
        db: AsyncSession,
        career_id,
        section_id,
    ) -> CareerCard | None:
        result = await db.execute(
            select(CareerCard)
            .where(
                CareerCard.career_id == career_id,
                CareerCard.section_id == section_id,
            )
        )
        return result.scalar_one_or_none()