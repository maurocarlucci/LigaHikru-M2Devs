from fastapi import APIRouter, HTTPException
from app.models.schemas import QuestionRequest, QuestionResponse, SearchRequest, SearchResponse, SearchResult
from app.services.rag_service import RAGService

router = APIRouter(prefix="/api/chat", tags=["Chat"])
rag_service = RAGService()


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Flujo 1: Preguntar → respuesta con citas a documentos
    
    Hace una pregunta y recibe una respuesta generada por IA con citas
    a los documentos fuente.
    """
    try:
        response = rag_service.ask_question(
            question=request.question,
            max_results=request.max_results,
            temperature=request.temperature
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando pregunta: {str(e)}")


@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Flujo 2: Buscar documento → retorna links/fragmentos relevantes
    
    Busca documentos y retorna fragmentos relevantes con links a los documentos.
    """
    try:
        results = rag_service.search_documents(
            query=request.query,
            max_results=request.max_results,
            filters=request.filters
        )
        return SearchResponse(
            results=results,
            total_results=len(results),
            query=request.query
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en búsqueda: {str(e)}")
