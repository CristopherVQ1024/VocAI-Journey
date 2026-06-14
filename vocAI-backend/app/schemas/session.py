from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from app.schemas.career import CareerSummary


# ─── Sesión ──────────────────────────────────────────────────────────────────

class SessionCreate(BaseModel):
    """
    Para iniciar una sesión.
    guest_token lo genera el frontend para usuarios no logueados.
    """
    guest_token: str | None = None


class SessionResponse(BaseModel):
    id: UUID
    user_id: UUID | None
    guest_token: str | None
    status: str
    started_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


# ─── Selección de carreras ───────────────────────────────────────────────────

class SelectCareersInput(BaseModel):
    """
    El alumno elige hasta 3 carreras para comparar.
    compatibility_score viene del test vocacional previo (0 si no hay test).
    """
    career_ids: list[UUID]              # exactamente 3
    compatibility_scores: dict[str, float] = {}  # {career_id: score}


class SelectedCareerResponse(BaseModel):
    id: UUID
    career_id: UUID
    compatibility_score: float
    selected_order: int
    career: CareerSummary

    model_config = {"from_attributes": True}


# ─── Respuesta por sección ───────────────────────────────────────────────────

class SectionAnswerInput(BaseModel):
    """Lo que el alumno envía al elegir 'Esta conectó más conmigo'."""
    section_id: UUID
    selected_career_id: UUID


class SectionAnswerResponse(BaseModel):
    id: UUID
    section_id: UUID
    selected_career_id: UUID
    score_awarded: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Ranking final ───────────────────────────────────────────────────────────

class RankingResultResponse(BaseModel):
    """Una posición del ranking con sus scores y justificación de IA."""
    ranking_position: int
    career: CareerSummary
    compatibility_score: float
    interaction_score: float
    final_score: float
    ai_justification: str | None

    model_config = {"from_attributes": True}


class FullRankingResponse(BaseModel):
    """Respuesta completa al terminar el journey."""
    session_id: UUID
    results: list[RankingResultResponse]


# ─── Guardar ranking ─────────────────────────────────────────────────────────

class SaveRankingInput(BaseModel):
    nombre: str   # "Mi ranking junio 2026"


class SavedRankingResponse(BaseModel):
    id: UUID
    nombre: str
    session_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}