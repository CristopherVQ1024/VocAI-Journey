import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Text, Enum as SAEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nombres: Mapped[str] = mapped_column(String(100), nullable=False)
    apellidos: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider: Mapped[str] = mapped_column(
        SAEnum("local", "google", name="provider_enum"),
        default="local",
        nullable=False,
    )
    profile_image: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relaciones
    vocational_sessions: Mapped[list["VocationalSession"]] = relationship(
        back_populates="user"
    )
    saved_rankings: Mapped[list["SavedRanking"]] = relationship(
        back_populates="user"
    )
    chatbot_conversations: Mapped[list["ChatbotConversation"]] = relationship(
        back_populates="user"
    )