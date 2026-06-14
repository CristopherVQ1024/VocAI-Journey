import uuid
from datetime import datetime
from sqlalchemy import (
    String, Integer, Text, Enum as SAEnum,
    DateTime, ForeignKey, Numeric,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class VocationalSession(Base):
    """
    Sesión del journey completo.
    Funciona tanto para usuarios logueados (user_id) como invitados (guest_token).
    """
    __tablename__ = "vocational_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # NULL si es invitado
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    # Token aleatorio para identificar sesiones de invitados (se guarda en localStorage)
    guest_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        SAEnum("in_progress", "completed", "abandoned", name="session_status_enum"),
        default="in_progress",
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relaciones
    user: Mapped["User | None"] = relationship(back_populates="vocational_sessions")
    selected_careers: Mapped[list["SessionSelectedCareer"]] = relationship(
        back_populates="session"
    )
    section_answers: Mapped[list["SessionSectionAnswer"]] = relationship(
        back_populates="session"
    )
    ranking_results: Mapped[list["SessionRankingResult"]] = relationship(
        back_populates="session"
    )
    saved_ranking: Mapped["SavedRanking | None"] = relationship(
        back_populates="session"
    )
    chatbot_conversations: Mapped[list["ChatbotConversation"]] = relationship(
        back_populates="session"
    )


class SessionSelectedCareer(Base):
    """
    Las 3 carreras que el alumno eligió para comparar al inicio del journey.
    Máximo 3 por sesión (validar en el router/service).
    """
    __tablename__ = "session_selected_careers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vocational_sessions.id"), nullable=False
    )
    career_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("careers.id"), nullable=False
    )
    # Score de afinidad que viene del test vocacional previo (puede ser 0 si no hay test)
    compatibility_score: Mapped[float] = mapped_column(
        Numeric(5, 2), default=0, nullable=False
    )
    # Orden en que el alumno las seleccionó (1, 2, 3)
    selected_order: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relaciones
    session: Mapped["VocationalSession"] = relationship(
        back_populates="selected_careers"
    )
    career: Mapped["Career"] = relationship(back_populates="session_selected")


class SessionSectionAnswer(Base):
    """
    Respuesta del alumno en cada paso del journey.
    En cada sección, elige 1 de las 3 carreras con la que 'conectó más'.
    Esa elección suma score_awarded puntos a esa carrera.
    """
    __tablename__ = "session_section_answers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vocational_sessions.id"), nullable=False
    )
    section_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("comparison_sections.id"), nullable=False
    )
    selected_career_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("careers.id"), nullable=False
    )
    # Puntos otorgados (ej: 10 por cada elección; puede variar si se añade gamificación)
    score_awarded: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relaciones
    session: Mapped["VocationalSession"] = relationship(back_populates="section_answers")
    section: Mapped["ComparisonSection"] = relationship(back_populates="section_answers")
    selected_career: Mapped["Career"] = relationship(back_populates="section_answers")


class SessionRankingResult(Base):
    """
    Resultado final generado al completar las 8 secciones.
    Una fila por cada carrera del ranking (3 filas por sesión completada).
    La justificación de IA se genera una vez y se guarda aquí.
    """
    __tablename__ = "session_ranking_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vocational_sessions.id"), nullable=False
    )
    career_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("careers.id"), nullable=False
    )
    ranking_position: Mapped[int] = mapped_column(Integer, nullable=False)  # 1, 2 o 3
    # Score del test vocacional original
    compatibility_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    # Score acumulado de las elecciones en el journey
    interaction_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    # Ponderación final: (compatibility * 0.4) + (interaction * 0.6) por ejemplo
    final_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    # Justificación generada por IA (solo para el #1, o para los 3 si se desea)
    ai_justification: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relaciones
    session: Mapped["VocationalSession"] = relationship(back_populates="ranking_results")
    career: Mapped["Career"] = relationship(back_populates="ranking_results")


class SavedRanking(Base):
    """
    Permite al usuario logueado guardar y nombrar su ranking para revisarlo después.
    Solo disponible si hay user_id en la sesión.
    """
    __tablename__ = "saved_rankings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vocational_sessions.id"), nullable=False
    )
    # Nombre que el usuario le da: "Ranking junio 2026", "Mi segunda prueba", etc.
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relaciones
    user: Mapped["User"] = relationship(back_populates="saved_rankings")
    session: Mapped["VocationalSession"] = relationship(back_populates="saved_ranking")