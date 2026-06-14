import uuid
from datetime import datetime
from sqlalchemy import String, Text, Enum as SAEnum, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class ChatbotKnowledge(Base):
    """
    Base de conocimiento del chatbot.
    El chatbot SOLO responde desde esta tabla — no inventa respuestas.
    career_id es NULL para preguntas generales (sobre la UTP, procesos, etc.)
    keywords se usa para buscar la respuesta correcta (búsqueda por similitud).
    """
    __tablename__ = "chatbot_knowledge"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # NULL = pregunta general; UUID = pregunta específica de esa carrera
    career_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("careers.id"), nullable=True
    )
    # Agrupación temática: "requisitos", "campo_laboral", "plan_estudios", etc.
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    # Lista de palabras clave separadas por coma para matching
    # Ej: "matemáticas,cálculo,números,matemática"
    keywords: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relaciones
    career: Mapped["Career | None"] = relationship(back_populates="chatbot_knowledge")


class ChatbotConversation(Base):
    """
    Agrupa los mensajes de una conversación con el chatbot.
    Funciona tanto para usuarios logueados como invitados (mediante session_id).
    """
    __tablename__ = "chatbot_conversations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # Ambos pueden ser NULL (invitado sin sesión activa)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vocational_sessions.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relaciones
    user: Mapped["User | None"] = relationship(back_populates="chatbot_conversations")
    session: Mapped["VocationalSession | None"] = relationship(
        back_populates="chatbot_conversations"
    )
    messages: Mapped[list["ChatbotMessage"]] = relationship(
        back_populates="conversation",
        order_by="ChatbotMessage.created_at",
    )


class ChatbotMessage(Base):
    """
    Mensajes individuales de una conversación.
    role='user' → lo que escribe el estudiante
    role='assistant' → la respuesta del chatbot
    """
    __tablename__ = "chatbot_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chatbot_conversations.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(
        SAEnum("user", "assistant", name="message_role_enum"),
        nullable=False,
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relaciones
    conversation: Mapped["ChatbotConversation"] = relationship(
        back_populates="messages"
    )