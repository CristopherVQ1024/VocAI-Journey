from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


# ─── Facultad ───────────────────────────────────────────────────────────────

class FacultyResponse(BaseModel):
    id: UUID
    nombre: str
    descripcion: str | None

    model_config = {"from_attributes": True}


# ─── Carrera ─────────────────────────────────────────────────────────────────

class CareerBase(BaseModel):
    nombre: str
    slug: str
    descripcion_corta: str | None
    duracion_semestres: int | None
    modalidad: str
    imagen_url: str | None
    color_hex: str | None
    demanda_laboral: str
    trabajo_remoto: bool
    salario_min: float | None
    salario_promedio: float | None
    salario_max: float | None


class CareerResponse(CareerBase):
    """Respuesta completa de una carrera con su facultad."""
    id: UUID
    faculty_id: UUID
    faculty: FacultyResponse
    activo: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CareerSummary(BaseModel):
    """Versión reducida para listados y cards."""
    id: UUID
    nombre: str
    slug: str
    descripcion_corta: str | None
    modalidad: str
    demanda_laboral: str
    trabajo_remoto: bool
    salario_promedio: float | None
    imagen_url: str | None
    color_hex: str | None
    faculty: FacultyResponse

    model_config = {"from_attributes": True}


# ─── Filtros para el listado ─────────────────────────────────────────────────

class CareerFilters(BaseModel):
    """Query params opcionales para filtrar carreras."""
    facultad: str | None = None
    modalidad: str | None = None          # presencial | semi_presencial | virtual
    demanda_laboral: str | None = None    # alta | media | baja
    trabajo_remoto: bool | None = None
    buscar: str | None = None             # búsqueda por nombre