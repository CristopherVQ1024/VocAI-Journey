from pydantic import BaseModel
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