from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.core.database import get_db
from app.models.chatbot import ChatbotKnowledge, ChatbotConversation, ChatbotMessage
from app.schemas.chatbot import ChatMessageInput, ChatbotReply, ChatConversationResponse

router = APIRouter()


@router.post("/message", response_model=ChatbotReply, status_code=201)
async def send_message(
    data: ChatMessageInput,
    db: AsyncSession = Depends(get_db),
):
    """
    El alumno envía un mensaje y el chatbot responde.
    Busca en chatbot_knowledge usando keywords.
    Si no encuentra respuesta, devuelve mensaje genérico.
    """
    # Crear conversación si no existe
    conversation = None
    if data.session_id:
        result = await db.execute(
            select(ChatbotConversation).where(
                ChatbotConversation.session_id == data.session_id
            )
        )
        conversation = result.scalar_one_or_none()

    if not conversation:
        conversation = ChatbotConversation(session_id=data.session_id)
        db.add(conversation)
        await db.flush()

    # Guardar mensaje del usuario
    user_msg = ChatbotMessage(
        conversation_id=conversation.id,
        role="user",
        message=data.message,
    )
    db.add(user_msg)

    # Buscar respuesta en la base de conocimiento
    reply_text, found = await _search_knowledge(data.message, db)

    # Guardar respuesta del asistente
    assistant_msg = ChatbotMessage(
        conversation_id=conversation.id,
        role="assistant",
        message=reply_text,
    )
    db.add(assistant_msg)
    await db.flush()

    return ChatbotReply(
        conversation_id=conversation.id,
        reply=reply_text,
        found_in_db=found,
    )


@router.get("/conversation/{conversation_id}", response_model=ChatConversationResponse)
async def get_conversation(conversation_id: str, db: AsyncSession = Depends(get_db)):
    """Recupera el historial completo de una conversación."""
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(ChatbotConversation)
        .where(ChatbotConversation.id == conversation_id)
        .options(selectinload(ChatbotConversation.messages))
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    return conversation


# ─── Búsqueda en base de conocimiento ───────────────────────────────────────

async def _search_knowledge(message: str, db: AsyncSession) -> tuple[str, bool]:
    """
    Busca en chatbot_knowledge usando las keywords.
    Retorna (respuesta, encontrado_en_bd).
    """
    # Extraer palabras clave del mensaje del usuario
    words = [w.lower().strip() for w in message.split() if len(w) > 3]

    if not words:
        return _default_reply(), False

    # Buscar en keywords de la BD (búsqueda simple por coincidencia)
    result = await db.execute(select(ChatbotKnowledge))
    all_knowledge = result.scalars().all()

    best_match = None
    best_score = 0

    for knowledge in all_knowledge:
        if not knowledge.keywords:
            continue
        kb_keywords = [k.lower().strip() for k in knowledge.keywords.split(",")]
        # Contar cuántas palabras del mensaje coinciden con las keywords
        score = sum(1 for word in words if any(word in kw or kw in word for kw in kb_keywords))
        if score > best_score:
            best_score = score
            best_match = knowledge

    if best_match and best_score > 0:
        return best_match.answer_markdown, True

    return _default_reply(), False


def _default_reply() -> str:
    return (
        "No encontré información específica sobre eso, pero puedo ayudarte "
        "con preguntas sobre carreras, requisitos, campo laboral y vida universitaria. "
        "¿Quieres saber algo específico sobre alguna carrera?"
    )