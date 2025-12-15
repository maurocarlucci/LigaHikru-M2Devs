import openai
from typing import List, Optional
from app.core.config import settings


class AzureOpenAIService:
    """Servicio para interactuar con Azure OpenAI"""
    
    def __init__(self):
        # Normalizar endpoint: quitar barra final si existe
        endpoint = settings.AZURE_OPENAI_ENDPOINT.rstrip('/')
        
        self.client = openai.AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=endpoint
        )
        self.deployment_name = settings.AZURE_OPENAI_DEPLOYMENT_NAME
        self.embedding_deployment = settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Genera embeddings para una lista de textos"""
        try:
            response = self.client.embeddings.create(
                model=self.embedding_deployment,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            raise Exception(f"Error generando embeddings: {str(e)}")
    
    def generate_chat_completion(
        self,
        messages: List[dict],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Genera una respuesta del chat"""
        try:
            # gpt-5.2-chat requiere max_completion_tokens y solo soporta temperature=1 (default)
            # No pasar temperature si no es 1.0 para evitar errores
            params = {
                "model": self.deployment_name,
                "messages": messages,
                "max_completion_tokens": max_tokens
            }
            
            # Solo agregar temperature si es diferente de 1.0 (aunque gpt-5.2-chat no lo soporta)
            # Por ahora, no pasamos temperature para evitar el error
            # if temperature != 1.0:
            #     params["temperature"] = temperature
            
            response = self.client.chat.completions.create(**params)
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generando respuesta: {str(e)}")
    
    def generate_rag_response(
        self,
        question: str,
        context: List[str],
        citations: List[dict],
        temperature: float = 0.7
    ) -> str:
        """Genera una respuesta RAG con contexto"""
        context_text = "\n\n".join([
            f"[Documento {i+1}]: {ctx}" 
            for i, ctx in enumerate(context)
        ])
        
        system_prompt = """Eres un asistente útil que responde preguntas basándote en documentos internos.
        Siempre cita los documentos cuando uses información de ellos.
        Si la información no está en los documentos, di que no tienes esa información.
        Responde de manera clara y concisa."""
        
        user_prompt = f"""Contexto de documentos:
{context_text}

Pregunta: {question}

Responde la pregunta basándote únicamente en el contexto proporcionado. 
Menciona los números de documento cuando cites información (ej: [Documento 1], [Documento 2])."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self.generate_chat_completion(messages, temperature=temperature)
