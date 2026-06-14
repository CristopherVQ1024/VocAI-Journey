from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


# ==========================================================
# Base para todos los modelos
# ==========================================================
class Base(DeclarativeBase):
    pass


# ==========================================================
# Variables globales (se inicializan luego)
# ==========================================================
engine: AsyncEngine | None = None
AsyncSessionLocal = None


# ==========================================================
# Inicialización de DB
# ==========================================================
def init_db():
    global engine, AsyncSessionLocal

    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True,        # Mostrar SQL en consola
        pool_size=5,
        max_overflow=10,
    )

    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


# ==========================================================
# Dependency de FastAPI
# ==========================================================
async def get_db() -> AsyncSession:
    if AsyncSessionLocal is None:
        raise RuntimeError(
            "Database no inicializada. Ejecuta init_db() primero."
        )

    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise