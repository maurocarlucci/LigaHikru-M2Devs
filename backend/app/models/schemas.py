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
