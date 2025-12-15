from typing import List
from app.services.azure_openai_service import AzureOpenAIService
from app.services.azure_search_service import AzureSearchService
from app.models.schemas import QuestionResponse, Citation


class RAGService:
    """Servicio RAG que combina búsqueda y generación"""
    
    def __init__(self):
        self.openai_service = AzureOpenAIService()
        self.search_service = AzureSearchService()
    
    def ask_question(
        self,
        question: str,
        max_results: int = 5,
        temperature: float = 0.7
    ) -> QuestionResponse:
        """Flujo 1: Preguntar → respuesta con citas a documentos"""
        
        # 1. Generar embedding de la pregunta
        question_embedding = self.openai_service.generate_embeddings([question])[0]
        
        # 2. Buscar documentos relevantes (búsqueda híbrida)
        search_results = self.search_service.search_documents(
            query=question,
            top=max_results,
            vector_query=question_embedding
        )
        
        if not search_results:
            return QuestionResponse(
                answer="No se encontraron documentos relevantes para tu pregunta.",
                citations=[],
                sources=[]
            )
        
        # 3. Convertir resultados a citations
        citations = self.search_service.search_to_citations(search_results)
        
        # 4. Extraer contextos para el LLM
        contexts = [result.get("content", "") for result in search_results]
        
        # 5. Generar respuesta con RAG
        answer = self.openai_service.generate_rag_response(
            question=question,
            context=contexts,
            citations=[cit.dict() for cit in citations],
            temperature=temperature
        )
        
        # 6. Extraer fuentes únicas
        sources = list(set([cit.document_name for cit in citations]))
        
        return QuestionResponse(
            answer=answer,
            citations=citations,
            sources=sources
        )
    
    def search_documents(
        self,
        query: str,
        max_results: int = 10,
        filters: dict = None
    ):
        """Flujo 2: Buscar documento → retorna links/fragmentos relevantes"""
        
        # 1. Generar embedding de la búsqueda
        query_embedding = self.openai_service.generate_embeddings([query])[0]
        
        # 2. Buscar documentos (búsqueda híbrida)
        filter_string = None
        if filters:
            # Convertir dict a string de filtro OData
            filter_parts = [f"{k} eq '{v}'" for k, v in filters.items()]
            filter_string = " and ".join(filter_parts)
        
        search_results = self.search_service.search_documents(
            query=query,
            top=max_results,
            filters=filter_string,
            vector_query=query_embedding
        )
        
        # 3. Convertir a SearchResult
        results = self.search_service.search_to_results(search_results)
        
        return results
