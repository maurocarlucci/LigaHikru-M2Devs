from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import chat, documents, auth

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API para búsqueda y consulta de documentos usando Azure AI",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS - Configuración flexible para desarrollo y producción
cors_origins = settings.CORS_ORIGINS.split(",") if "," in settings.CORS_ORIGINS else [settings.CORS_ORIGINS]
# Si es "*", mantener como lista con "*"
if settings.CORS_ORIGINS.strip() == "*":
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
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
