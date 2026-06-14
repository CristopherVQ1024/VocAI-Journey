import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class ComparisonSection(Base):
    """
    Define los 8 pasos del journey de comparación.
    Ej: orden=1 → '¿De qué trata la carrera?'
    """
    __tablename__ = "comparison_sections"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    # slug amigable para la URL: "de-que-trata", "dia-de-trabajo", etc.
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    orden: Mapped[int] = mapped_column(Integer, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relaciones
    career_cards: Mapped[list["CareerCard"]] = relationship(
        back_populates="section"
    )
    section_answers: Mapped[list["SessionSectionAnswer"]] = relationship(
        back_populates="section"
    )


class CareerCard(Base):
    """
    Tabla central del sistema.
    Cada fila = el contenido markdown de UNA carrera para UNA sección.
    Ej: carrera=Sistemas, sección='¿Qué hace un profesional?' → markdown con la info.
    """
    __tablename__ = "career_cards"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    career_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("careers.id"), nullable=False
    )
    section_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("comparison_sections.id"), nullable=False
    )
    # Contenido en markdown simplificado que el frontend renderiza
    markdown_content: Mapped[str] = mapped_column(Text, nullable=False)
    orden: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relaciones
    career: Mapped["Career"] = relationship(back_populates="career_cards")
    section: Mapped["ComparisonSection"] = relationship(back_populates="career_cards")