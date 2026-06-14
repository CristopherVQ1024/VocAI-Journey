from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime


# ─── Input ──────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    """Lo que el usuario envía al registrarse."""
    nombres: str
    apellidos: str | None = None
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """Lo que el usuario envía al hacer login."""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Campos que el usuario puede actualizar en su perfil."""
    nombres: str | None = None
    apellidos: str | None = None
    profile_image: str | None = None


# ─── Output ─────────────────────────────────────────────────────────────────

class UserResponse(BaseModel):
    """Lo que la API devuelve al consultar un usuario."""
    id: UUID
    nombres: str
    apellidos: str | None
    email: str
    provider: str
    profile_image: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Respuesta del login con el JWT."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse