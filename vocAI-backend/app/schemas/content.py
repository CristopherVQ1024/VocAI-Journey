from pydantic import BaseModel
from uuid import UUID


# ─── Mi Primer Día ───────────────────────────────────────────────────────────

class ExperienceContentResponse(BaseModel):
    """
    Un bloque de contenido del módulo 'Mi Primer Día'.
    El frontend renderiza markdown_content con un parser de markdown.
    """
    id: UUID
    categoria: str
    titulo: str
    markdown_content: str
    orden: int

    model_config = {"from_attributes": True}


class ExperienceContentByCategory(BaseModel):
    """
    Agrupa el contenido por categoría para mostrarlo en subsecciones.
    Ej: categoria='fears' → lista de miedos comunes
    """
    categoria: str
    items: list[ExperienceContentResponse]


# ─── UTP ─────────────────────────────────────────────────────────────────────

class UtpContentResponse(BaseModel):
    """Un bloque de info institucional de la UTP."""
    id: UUID
    categoria: str
    titulo: str
    markdown_content: str
    orden: int

    model_config = {"from_attributes": True}


class UtpContentByCategory(BaseModel):
    """
    Agrupa el contenido de UTP por categoría.
    Ej: categoria='laboratorios' → info de los labs
    """
    categoria: str
    items: list[UtpContentResponse]