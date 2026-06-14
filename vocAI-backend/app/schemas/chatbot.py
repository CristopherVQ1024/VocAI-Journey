from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


# ─── Input ───────────────────────────────────────────────────────────────────

class ChatMessageInput(BaseModel):
    """Lo que el alumno envía al chatbot."""
    message: str
    # Opcional: si está en el journey, para contextualizar la respuesta
    session_id: UUID | None = None


# ─── Output ──────────────────────────────────────────────────────────────────

class ChatMessageResponse(BaseModel):
    id: UUID
    role: str           # "user" | "assistant"
    message: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatConversationResponse(BaseModel):
    """Conversación completa con todos sus mensajes."""
    id: UUID
    created_at: datetime
    messages: list[ChatMessageResponse]

    model_config = {"from_attributes": True}


class ChatbotReply(BaseModel):
    """
    Respuesta inmediata del chatbot a un mensaje.
    found_in_db indica si la respuesta vino de chatbot_knowledge
    o si no se encontró match.
    """
    conversation_id: UUID
    reply: str
    found_in_db: bool