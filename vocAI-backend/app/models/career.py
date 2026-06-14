import uuid
from datetime import datetime
from sqlalchemy import (
    String, Text, Integer, Boolean, Enum as SAEnum,
    DateTime, ForeignKey, Numeric,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Faculty(Base):
    __tablename__ = "faculties"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relaciones
    careers: Mapped[list["Career"]] = relationship(back_populates="faculty")


class Career(Base):
    __tablename__ = "careers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    faculty_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("faculties.id"), nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    descripcion_corta: Mapped[str | None] = mapped_column(Text, nullable=True)
    duracion_semestres: Mapped[int | None] = mapped_column(Integer, nullable=True)
    modalidad: Mapped[str] = mapped_column(
        SAEnum(
            "presencial", "semi_presencial", "virtual",
            name="modalidad_enum"
        ),
        nullable=False,
    )
    imagen_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Color para la card visual en el frontend (ej: "#3B82F6")
    color_hex: Mapped[str | None] = mapped_column(String(7), nullable=True)
    demanda_laboral: Mapped[str] = mapped_column(
        SAEnum("alta", "media", "baja", name="demanda_enum"),
        nullable=False,
    )
    trabajo_remoto: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    salario_min: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    salario_promedio: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    salario_max: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relaciones
    faculty: Mapped["Faculty"] = relationship(back_populates="careers")
    career_cards: Mapped[list["CareerCard"]] = relationship(back_populates="career")
    session_selected: Mapped[list["SessionSelectedCareer"]] = relationship(
        back_populates="career"
    )
    section_answers: Mapped[list["SessionSectionAnswer"]] = relationship(
        back_populates="selected_career"
    )
    ranking_results: Mapped[list["SessionRankingResult"]] = relationship(
        back_populates="career"
    )
    chatbot_knowledge: Mapped[list["ChatbotKnowledge"]] = relationship(
        back_populates="career"
    )