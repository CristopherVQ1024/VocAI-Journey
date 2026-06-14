import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings


async def check_tables():
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False
    )

    async with engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))

        tables = result.fetchall()

        print("\n📦 Tablas encontradas:\n")

        for table in tables:
            print(f"✅ {table[0]}")

    await engine.dispose()


asyncio.run(check_tables())