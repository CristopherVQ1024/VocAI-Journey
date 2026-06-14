from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.chatbot import ChatbotKnowledge, ChatbotConversation, ChatbotMessage


class ChatbotService:

    @staticmethod
    async def get_or_create_conversation(
        db: AsyncSession,
        session_id=None,
        user_id=None,
    ) -> ChatbotConversation:
        """
        Retorna la conversación activa de una sesión o crea una nueva.
        Así el historial se mantiene mientras dura el journey.
        """
        if session_id:
            result = await db.execute(
                select(ChatbotConversation).where(
                    ChatbotConversation.session_id == session_id
                )
            )
            conversation = result.scalar_one_or_none()
            if conversation:
                return conversation

        conversation = ChatbotConversation(
            session_id=session_id,
            user_id=user_id,
        )
        db.add(conversation)
        await db.flush()
        return conversation

    @staticmethod
    async def save_message(
        db: AsyncSession,
        conversation_id,
        role: str,
        message: str,
    ) -> ChatbotMessage:
        """Guarda un mensaje (user o assistant) en la conversación."""
        msg = ChatbotMessage(
            conversation_id=conversation_id,
            role=role,
            message=message,
        )
        db.add(msg)
        await db.flush()
        return msg

    @staticmethod
    async def search_knowledge(
        db: AsyncSession,
        user_message: str,
        career_id=None,
    ) -> tuple[str, bool]:
        """
        Busca la mejor respuesta en chatbot_knowledge.

        Estrategia:
        1. Si hay career_id, prioriza respuestas de esa carrera.
        2. Compara palabras del mensaje con las keywords de cada registro.
        3. Retorna (respuesta_markdown, encontrado_en_bd).
        """
        # Palabras relevantes del mensaje (más de 3 letras)
        words = [w.lower().strip("¿?.,!") for w in user_message.split() if len(w) > 3]

        if not words:
            return ChatbotService._default_reply(), False

        # Traer toda la base de conocimiento
        result = await db.execute(select(ChatbotKnowledge))
        all_knowledge = result.scalars().all()

        best_match: ChatbotKnowledge | None = None
        best_score = 0

        for entry in all_knowledge:
            if not entry.keywords:
                continue

            kb_keywords = [k.lower().strip() for k in entry.keywords.split(",")]

            # Calcular score de coincidencia
            score = sum(
                1 for word in words
                if any(word in kw or kw in word for kw in kb_keywords)
            )

            # Bonus si coincide con la carrera del contexto
            if career_id and str(entry.career_id) == str(career_id):
                score += 2

            if score > best_score:
                best_score = score
                best_match = entry

        if best_match and best_score > 0:
            return best_match.answer_markdown, True

        return ChatbotService._default_reply(), False

    @staticmethod
    def _default_reply() -> str:
        return (
            "No encontré información específica sobre eso en mi base de conocimiento. "
            "Puedo ayudarte con preguntas sobre carreras, requisitos de ingreso, "
            "campo laboral, sueldos y vida universitaria. ¿Qué te gustaría saber?"
        )