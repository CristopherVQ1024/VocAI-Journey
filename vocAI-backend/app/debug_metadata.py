from app.core.database import Base

# Importar TODOS los modelos
from app.models.user import User
from app.models.career import Faculty, Career
from app.models.comparison import ComparisonSection, CareerCard
from app.models.session import (
    VocationalSession,
    SessionSelectedCareer,
    SessionSectionAnswer,
    SessionRankingResult,
    SavedRanking,
)
from app.models.content import (
    UniversityExperienceContent,
    UtpContent,
)
from app.models.chatbot import (
    ChatbotKnowledge,
    ChatbotConversation,
    ChatbotMessage,
)

print("\n📦 Tablas registradas:\n")

for table in Base.metadata.tables.keys():
    print(f"✅ {table}")