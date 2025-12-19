from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from typing import List, Optional, Dict
import re
from app.core.config import settings
from app.models.schemas import SearchResult, Citation


class AzureSearchService:
    """Servicio para interactuar con Azure AI Search"""
    
    def __init__(self):
        self.client = SearchClient(
            endpoint=settings.AZURE_SEARCH_ENDPOINT,
            index_name=settings.AZURE_SEARCH_INDEX_NAME,
            credential=AzureKeyCredential(settings.AZURE_SEARCH_API_KEY)
        )
    
    def search_documents(
        self,
        query: str,
        top: int = 10,
        filters: Optional[str] = None,
        vector_query: Optional[List[float]] = None
    ) -> List[Dict]:
        """Busca documentos usando búsqueda híbrida (texto + vectorial)"""
        vector_queries = None
        
        # Si hay vector query, crear VectorizedQuery
        if vector_query:
            vector_queries = [
                VectorizedQuery(
                    vector=vector_query,
                    k_nearest_neighbors=top,
                    fields="contentVector"
                )
            ]
        
        try:
            # Búsqueda híbrida: texto + vectorial
            results = self.client.search(
                search_text=query if query else None,
                vector_queries=vector_queries,
                top=top,
                filter=filters,
                include_total_count=True
            )
            return list(results)
        except Exception as e:
            raise Exception(f"Error en búsqueda: {str(e)}")
    
    def search_to_results(self, search_results: List[Dict]) -> List[SearchResult]:
        """Convierte resultados de búsqueda a SearchResult"""
        results = []
        for result in search_results:
            results.append(SearchResult(
                document_name=result.get("documentName", "Desconocido"),
                content=result.get("content", ""),
                score=result.get("@search.score", 0.0),
                source_url=result.get("sourceUrl"),
                metadata={
                    "page_number": result.get("pageNumber"),
                    "chunk_index": result.get("chunkIndex"),
                    **{k: v for k, v in result.items() if k.startswith("metadata_")}
                }
            ))
        return results
    
    def search_to_citations(self, search_results: List[Dict]) -> List[Citation]:
        """Convierte resultados de búsqueda a Citations"""
        citations = []
        for result in search_results:
            citations.append(Citation(
                document_name=result.get("documentName", "Desconocido"),
                content=result.get("content", ""),
                page_number=result.get("pageNumber"),
                score=result.get("@search.score", 0.0),
                source_url=result.get("sourceUrl")
            ))
        return citations
    
    def upload_document_chunk(
        self,
        document_name: str,
        content: str,
        content_vector: List[float],
        chunk_index: int,
        page_number: Optional[int] = None,
        source_url: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Sube un chunk de documento al índice"""
        # Validar dimensiones del vector
        if not content_vector:
            raise Exception("El vector de embeddings está vacío")
        
        if len(content_vector) != 1536:
            raise Exception(f"Dimensiones incorrectas del vector: {len(content_vector)}. Se esperan 1536 dimensiones.")
        
        # Limpiar el nombre del documento para el ID (solo letras, dígitos, guiones y guiones bajos)
        # Reemplazar todos los caracteres no permitidos
        safe_doc_name = re.sub(r'[^a-zA-Z0-9_-]', '_', document_name)
        # Limpiar guiones bajos múltiples
        safe_doc_name = re.sub(r'_+', '_', safe_doc_name)
        # Eliminar guiones bajos al inicio y final
        safe_doc_name = safe_doc_name.strip('_')
        
        doc = {
            "id": f"{safe_doc_name}_{chunk_index}",
            "documentName": document_name,
            "content": content,
            "contentVector": content_vector,
            "chunkIndex": chunk_index,
            "sourceUrl": source_url or ""
        }
        
        if page_number is not None:
            doc["pageNumber"] = page_number
        
        # Nota: Los campos metadata no se incluyen porque no están definidos en el esquema del índice
        # Si necesitas metadata, debes agregar los campos al esquema del índice primero
        
        try:
            result = self.client.upload_documents(documents=[doc])
            # Verificar si hubo errores en la respuesta
            if result and len(result) > 0:
                for r in result:
                    if not r.succeeded:
                        raise Exception(f"Error en respuesta de Azure: {r.error_message}")
        except Exception as e:
            error_msg = str(e)
            # Mejorar el mensaje de error
            if "index" in error_msg.lower() and "not found" in error_msg.lower():
                raise Exception(f"El índice '{settings.AZURE_SEARCH_INDEX_NAME}' no existe. Ejecuta 'python create_index.py' primero.")
            elif "dimension" in error_msg.lower():
                raise Exception(f"Error de dimensiones: {error_msg}")
            else:
                raise Exception(f"Error subiendo chunk a Azure AI Search: {error_msg}")
    
    def delete_document_chunks(self, document_name: str) -> int:
        """
        Elimina todos los chunks de un documento del índice.
        Busca por documentName y elimina todos los chunks encontrados.
        Retorna el número de chunks eliminados.
        """
        try:
            # Buscar todos los chunks del documento por nombre exacto
            # Usamos búsqueda de texto en el campo documentName
            results = self.client.search(
                search_text=document_name,
                search_fields=["documentName"],
                select=["id", "documentName"],
                top=1000  # Máximo de chunks a eliminar por documento
            )
            
            # Recolectar solo los IDs donde el documentName coincide exactamente
            chunk_ids = [
                result["id"] for result in results 
                if result.get("documentName") == document_name
            ]
            
            if not chunk_ids:
                return 0
            
            # Eliminar los chunks en lotes
            documents_to_delete = [{"id": chunk_id} for chunk_id in chunk_ids]
            result = self.client.delete_documents(documents=documents_to_delete)
            
            # Contar eliminaciones exitosas
            deleted_count = sum(1 for r in result if r.succeeded)
            
            return deleted_count
            
        except Exception as e:
            raise Exception(f"Error eliminando chunks del índice: {str(e)}")
