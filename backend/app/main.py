from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import chat, documents

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API para búsqueda y consulta de documentos usando Azure AI",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(chat.router)
app.include_router(documents.router)


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "LigaHikru - Documentos AI API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}
