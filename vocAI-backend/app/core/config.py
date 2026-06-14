from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Base de datos
    DATABASE_URL: str

    # JWT Auth
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # IA (Anthropic) - se usará después
    ANTHROPIC_API_KEY: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instancia global - se importa desde cualquier módulo así:
# from app.core.config import settings
settings = Settings()