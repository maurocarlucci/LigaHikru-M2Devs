from typing import List
import re
from app.services.azure_openai_service import AzureOpenAIService
from app.services.azure_search_service import AzureSearchService
from app.models.schemas import QuestionResponse, Citation


class RAGService:
    """Servicio RAG que combina búsqueda y generación"""
    
    # Umbral mínimo de relevancia para incluir un documento
    MIN_RELEVANCE_SCORE = 0.02  # 2% - ajustable según necesidad
    
    def __init__(self):
        self.openai_service = AzureOpenAIService()
        self.search_service = AzureSearchService()
    
    def _filter_citations_by_score(self, citations: List[Citation], min_score: float) -> List[Citation]:
        """Filtra citas por score mínimo de relevancia"""
        return [cit for cit in citations if cit.score >= min_score]
    
    def _filter_citations_by_usage(self, citations: List[Citation], answer: str) -> List[Citation]:
        """
        Filtra citas para incluir SOLO los documentos que fueron realmente 
        citados/mencionados en la respuesta generada.
        """
        used_citations = []
        answer_lower = answer.lower()
        
        for cit in citations:
            doc_name = cit.document_name
            doc_name_lower = doc_name.lower()
            
            # Verificar si el documento fue citado en la respuesta
            # Patrones comunes de citación:
            # - [DOCUMENTO.pdf, Página X]
            # - [DOCUMENTO.pdf]
            # - DOCUMENTO.pdf
            # - "documento" (sin extensión)
            
            # Patrón 1: Citación con corchetes [nombre.pdf...]
            if f"[{doc_name}" in answer or f"[{doc_name_lower}" in answer_lower:
                used_citations.append(cit)
                continue
            
            # Patrón 2: Nombre del documento mencionado directamente
            if doc_name_lower in answer_lower:
                used_citations.append(cit)
                continue
            
            # Patrón 3: Nombre sin extensión (ej: "MANUAL DE ONBOARDING" sin .pdf)
            doc_name_no_ext = re.sub(r'\.(pdf|txt|md)$', '', doc_name_lower, flags=re.IGNORECASE)
            if doc_name_no_ext and len(doc_name_no_ext) > 3 and doc_name_no_ext in answer_lower:
                used_citations.append(cit)
                continue
        
        return used_citations
    
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
        all_citations = self.search_service.search_to_citations(search_results)
        
        # 4. FILTRO A: Aplicar umbral de score mínimo
        # Esto elimina documentos con baja relevancia semántica
        relevant_citations = self._filter_citations_by_score(all_citations, self.MIN_RELEVANCE_SCORE)
        
        # Si no hay citas relevantes después del filtro, usar las originales para el contexto
        # pero no las mostraremos si el LLM no las usa
        citations_for_context = relevant_citations if relevant_citations else all_citations
        
        # 5. Extraer contextos para el LLM (solo de documentos relevantes)
        relevant_doc_names = {cit.document_name for cit in citations_for_context}
        contexts = []
        context_citations = []
        
        for result in search_results:
            doc_name = result.get("documentName", "")
            if doc_name in relevant_doc_names:
                contexts.append(result.get("content", ""))
                # Encontrar la cita correspondiente
                for cit in citations_for_context:
                    if cit.document_name == doc_name:
                        context_citations.append(cit)
                        break
        
        # 6. Generar respuesta con RAG
        answer = self.openai_service.generate_rag_response(
            question=question,
            context=contexts,
            citations=[cit.dict() for cit in context_citations],
            temperature=temperature
        )
        
        # 7. FILTRO B: Solo incluir citas de documentos REALMENTE usados en la respuesta
        # Esto asegura que las fuentes mostradas correspondan al contenido generado
        used_citations = self._filter_citations_by_usage(citations_for_context, answer)
        
        # Si no hay citas usadas, es probablemente un saludo o pregunta fuera de tema
        if not used_citations:
            return QuestionResponse(
                answer=answer,
                citations=[],
                sources=[]
            )
        
        # 8. Extraer fuentes únicas de las citas realmente usadas
        sources = list(set([cit.document_name for cit in used_citations]))
        
        return QuestionResponse(
            answer=answer,
            citations=used_citations,
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
