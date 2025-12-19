from fastapi import APIRouter, HTTPException, UploadFile, File
from app.models.schemas import DocumentUploadResponse
from app.services.document_processor import DocumentProcessor
from app.services.azure_blob_service import AzureBlobService
from app.services.azure_search_service import AzureSearchService
import os

router = APIRouter(prefix="/api/documents", tags=["Documents"])
document_processor = DocumentProcessor()
blob_service = AzureBlobService()
search_service = AzureSearchService()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Sube y procesa un documento (PDF o texto).
    
    El documento se:
    1. Sube a Azure Blob Storage
    2. Procesa y divide en chunks
    3. Genera embeddings
    4. Indexa en Azure AI Search
    """
    try:
        # Leer contenido del archivo
        file_content = await file.read()
        filename = file.filename
        
        # Validar extensión
        if not filename:
            raise HTTPException(status_code=400, detail="Nombre de archivo requerido")
        
        ext = os.path.splitext(filename)[1].lower()
        
        # Subir a Blob Storage
        blob_url = blob_service.upload_file(file_content, filename)
        
        # Procesar documento
        if ext == '.pdf':
            chunks = document_processor.process_pdf(file_content, filename)
        elif ext in ['.txt', '.md']:
            text_content = file_content.decode('utf-8')
            chunks = document_processor.process_text(text_content, filename)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Formato no soportado: {ext}. Use PDF, TXT o MD"
            )
        
        # Verificar que se generaron chunks
        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No se pudo extraer contenido del documento. Verifica que el PDF tenga texto extraíble (no sea solo imágenes)."
            )
        
        # Indexar chunks
        chunks_processed = document_processor.index_document(chunks)
        
        if chunks_processed == 0:
            raise HTTPException(
                status_code=500,
                detail=f"El documento se procesó ({len(chunks)} chunks generados) pero no se pudieron indexar. Verifica la configuración de Azure AI Search."
            )
        
        return DocumentUploadResponse(
            filename=filename,
            status="success",
            chunks_processed=chunks_processed,
            message=f"Documento procesado exitosamente. {chunks_processed} chunks indexados."
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando documento: {str(e)}")


@router.get("/list")
async def list_documents():
    """Lista todos los documentos en el storage"""
    try:
        files = blob_service.list_files()
        return {"documents": files, "total": len(files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando documentos: {str(e)}")


@router.delete("/{filename}")
async def delete_document(filename: str):
    """
    Elimina un documento del storage y sus chunks del índice de búsqueda.
    
    1. Elimina los chunks del documento en Azure AI Search
    2. Elimina el archivo de Azure Blob Storage
    """
    try:
        # 1. Eliminar chunks del índice de búsqueda
        chunks_deleted = search_service.delete_document_chunks(filename)
        
        # 2. Eliminar archivo del blob storage
        blob_service.delete_file(filename)
        
        return {
            "message": f"Documento {filename} eliminado exitosamente",
            "chunks_deleted": chunks_deleted
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando documento: {str(e)}")
