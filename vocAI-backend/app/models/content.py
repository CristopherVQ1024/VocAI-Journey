import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, Boolean, Enum as SAEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class UniversityExperienceContent(Base):
    """
    Contenido del módulo 'Mi Primer Día'.
    Es independiente de carrera — aplica a todos los estudiantes.
    Las categorías mapean directo a las subsecciones del frontend.
    """
    __tablename__ = "university_experience_content"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    categoria: Mapped[str] = mapped_column(
        SAEnum(
            "first_day",   # Tu primer día: salones, horarios, orientación
            "friends",     # Hacer amigos
            "classes",     # Cómo son las clases
            "teachers",    # Cómo son los profesores
            "exams",       # Exámenes y evaluaciones
            "campus",      # Conocer el campus
            "clubs",       # Clubs y actividades extracurriculares
            "tips",        # Consejos reales de alumnos
            "fears",       # Miedos comunes y cómo afrontarlos
            name="experience_categoria_enum",
        ),
        nullable=False,
    )
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    markdown_content: Mapped[str] = mapped_column(Text, nullable=False)
    orden: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )


class UtpContent(Base):
    """
    Información resumida de la UTP para la sección institucional.
    Contenido estático gestionado desde el backend (sin necesidad de CMS externo).
    """
    __tablename__ = "utp_content"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    categoria: Mapped[str] = mapped_column(
        SAEnum(
            "laboratorios",   # Laboratorios modernos por carrera
            "convenios",      # Convenios con empresas nacionales e internacionales
            "empleabilidad",  # % de empleabilidad, estadísticas
            "bienestar",      # Servicios de bienestar estudiantil
            "tutorias",       # Sistema de tutorías académicas
            "bolsa_laboral",  # Bolsa de trabajo UTP
            "internacional",  # Intercambios y programas internacionales
            name="utp_categoria_enum",
        ),
        nullable=False,
    )
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    markdown_content: Mapped[str] = mapped_column(Text, nullable=False)
    orden: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )