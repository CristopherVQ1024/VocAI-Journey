from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


# ─── Sección ─────────────────────────────────────────────────────────────────

class ComparisonSectionResponse(BaseModel):
    """Un paso del journey (ej: orden=1 '¿De qué trata la carrera?')"""
    id: UUID
    nombre: str
    slug: str
    descripcion: str | None
    orden: int

    model_config = {"from_attributes": True}


# ─── Career Card ─────────────────────────────────────────────────────────────

class CareerCardResponse(BaseModel):
    """Contenido markdown de una carrera para una sección específica."""
    id: UUID
    career_id: UUID
    section_id: UUID
    markdown_content: str
    orden: int

    model_config = {"from_attributes": True}


class CareerCardWithSection(CareerCardResponse):
    """Card con info de su sección incluida (útil para el journey)."""
    section: ComparisonSectionResponse

    model_config = {"from_attributes": True}

# ─── Career Card Admin ──────────────────────────────────────────────────────

class CareerCardAdminResponse(BaseModel):
    """
    Respuesta completa para panel admin.
    """
    id: UUID
    career_id: UUID
    section_id: UUID
    markdown_content: str
    orden: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CareerCardCreate(BaseModel):
    """
    Crear card de carrera.
    """
    career_id: UUID
    section_id: UUID
    markdown_content: str = Field(..., min_length=5)
    orden: int = 1
    is_active: bool = True


class CareerCardUpdate(BaseModel):
    """
    Editar card parcialmente.
    """
    career_id: UUID | None = None
    section_id: UUID | None = None
    markdown_content: str | None = None
    orden: int | None = None
    is_active: bool | None = None

# ─── Paso del journey ────────────────────────────────────────────────────────

class ComparisonStepResponse(BaseModel):
    """
    Lo que el frontend recibe en cada paso del journey.
    Incluye la sección actual y las 3 cards de las carreras seleccionadas.
    """
    section: ComparisonSectionResponse
    cards: list[CareerCardResponse]
    total_steps: int
    current_step: int

# ─────────────────────────────────────────────────────
# Comparison Section Admin
# ─────────────────────────────────────────────────────

class ComparisonSectionCreate(BaseModel):
    nombre: str = Field(..., max_length=150)
    slug: str = Field(..., max_length=150)
    descripcion: str | None = None
    orden: int = Field(..., ge=1)
    activo: bool = True


class ComparisonSectionUpdate(BaseModel):
    nombre: str | None = Field(None, max_length=150)
    slug: str | None = Field(None, max_length=150)
    descripcion: str | None = None
    orden: int | None = Field(None, ge=1)
    activo: bool | None = None


class ComparisonSectionAdminResponse(BaseModel):
    id: UUID
    nombre: str
    slug: str
    descripcion: str | None
    orden: int
    activo: bool

    model_config = {"from_attributes": True}