from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# IMPORTA init_db
from app.core.database import init_db

app = FastAPI(
    title="VocAI UTP - API",
    description="Plataforma de acompañamiento vocacional post-test para UTP",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ==========================================================
# Inicializar base de datos
# ==========================================================
init_db()


# ==========================================================
# CORS
# ==========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# Routers
# ==========================================================
from app.routers import (
    auth,
    careers,
    comparison,
    ranking,
    first_day,
    utp,
    chatbot,
)

app.include_router(auth.router,       prefix="/api/auth",       tags=["Auth"])
app.include_router(careers.router,    prefix="/api/careers",    tags=["Carreras"])
app.include_router(comparison.router, prefix="/api/comparison", tags=["Comparación"])
app.include_router(ranking.router,    prefix="/api/ranking",    tags=["Ranking"])
app.include_router(first_day.router,  prefix="/api/first-day",  tags=["Mi Primer Día"])
app.include_router(utp.router,        prefix="/api/utp",        tags=["UTP"])
app.include_router(chatbot.router,    prefix="/api/chatbot",    tags=["Chatbot"])


# ==========================================================
# Health Check
# ==========================================================
@app.get("/", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "message": "VocAI API corriendo"
    }