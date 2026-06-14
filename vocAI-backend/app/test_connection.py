import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings


async def test_connection():
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True,
    )

    try:
        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT version();")
            )

            print("✅ Conexión exitosa")
            print(result.scalar())

    except Exception as e:
        print("❌ Error:")
        print(repr(e))

    finally:
        await engine.dispose()


asyncio.run(test_connection())