from fastapi import APIRouter, HTTPException
from app.services.azure_sql_service import AzureSQLService
from typing import Optional

router = APIRouter(prefix="/api/history", tags=["History"])
sql_service = AzureSQLService()


@router.get("/questions")
async def get_question_history(limit: int = 10):
    """Obtiene historial de preguntas"""
    try:
        history = sql_service.get_question_history(limit=limit)
        return {"history": history, "total": len(history)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo historial: {str(e)}")


@router.get("/documents")
async def get_documents_with_metadata():
    """Obtiene lista de documentos con metadata de SQL"""
    try:
        documents = sql_service.get_documents_list()
        return {"documents": documents, "total": len(documents)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo documentos: {str(e)}")
