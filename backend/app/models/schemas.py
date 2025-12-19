from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class DocumentChunk(BaseModel):
    """Fragmento de documento con metadata"""
    content: str
    source: str
    page_number: Optional[int] = None
    chunk_index: int
    metadata: Optional[dict] = None


class Citation(BaseModel):
    """Cita a un documento"""
    document_name: str
    content: str
    page_number: Optional[int] = None
    score: float
    source_url: Optional[str] = None


class QuestionRequest(BaseModel):
    """Request para hacer una pregunta"""
    question: str
    max_results: int = 5
    temperature: float = 0.7


class QuestionResponse(BaseModel):
    """Respuesta con citas a documentos"""
    answer: str
    citations: List[Citation]
    sources: List[str]


class SearchRequest(BaseModel):
    """Request para buscar documentos"""
    query: str
    max_results: int = 10
    filters: Optional[dict] = None


class SearchResult(BaseModel):
    """Resultado de búsqueda de documento"""
    document_name: str
    content: str
    score: float
    source_url: Optional[str] = None
    metadata: Optional[dict] = None


class SearchResponse(BaseModel):
    """Respuesta de búsqueda"""
    results: List[SearchResult]
    total_results: int
    query: str


class DocumentUploadResponse(BaseModel):
    """Respuesta de carga de documento"""
    filename: str
    status: str
    chunks_processed: int
    message: str


# Authentication Schemas
class UserBase(BaseModel):
    """Base de usuario"""
    email: str
    username: str


class UserCreate(UserBase):
    """Crear usuario"""
    password: str


class User(UserBase):
    """Usuario"""
    id: int
    role: str = "user"  # "admin" o "user"
    created_at: Optional[datetime] = None
    is_active: bool = True
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token de acceso"""
    access_token: str
    token_type: str = "bearer"
    user: User


class SignUpRequest(BaseModel):
    """Request para registro"""
    email: str
    username: str
    password: str


class LoginRequest(BaseModel):
    """Request para login"""
    email: str
    password: str