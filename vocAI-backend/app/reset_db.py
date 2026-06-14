import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings


async def reset():
    engine = create_async_engine(settings.DATABASE_URL)

    async with engine.begin() as conn:
        await conn.execute(
            text("DROP TABLE IF EXISTS alembic_version")
        )

    print("✅ Tabla alembic_version eliminada")

    await engine.dispose()


asyncio.run(reset())