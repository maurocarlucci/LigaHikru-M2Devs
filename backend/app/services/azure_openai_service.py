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
        # Build context with actual document names and page numbers
        context_parts = []
        for i, ctx in enumerate(context):
            doc_name = citations[i].get("document_name", f"Documento {i+1}") if i < len(citations) else f"Documento {i+1}"
            page_num = citations[i].get("page_number") if i < len(citations) else None
            page_info = f" (Página {page_num})" if page_num else ""
            context_parts.append(f"[{doc_name}{page_info}]: {ctx}")
        
        context_text = "\n\n".join(context_parts)
        
        system_prompt = """Eres un asistente especializado ÚNICAMENTE en responder preguntas sobre los documentos internos de la organización.

REGLAS ESTRICTAS:
1. SOLO puedes responder preguntas relacionadas con el contenido de los documentos proporcionados.
2. Si el usuario envía un saludo simple (Hola, Buenos días, etc.), responde amablemente y recuérdale que estás aquí para ayudarle con preguntas sobre los documentos.
3. Si el usuario hace una pregunta que NO está relacionada con los documentos (ej: Pokémon, clima, deportes, temas generales), responde educadamente: "Lo siento, solo puedo ayudarte con preguntas relacionadas con los documentos de la organización. ¿Tienes alguna pregunta sobre ellos?"
4. NO respondas preguntas de conocimiento general que no estén en los documentos, aunque sepas la respuesta.
5. Cuando la pregunta SÍ esté relacionada con los documentos, responde basándote en el contexto y cita usando el formato [Nombre del documento.pdf, Página X].
6. Responde de manera clara y concisa."""
        
        user_prompt = f"""Contexto de documentos disponibles:
{context_text}

Mensaje del usuario: {question}

Instrucciones:
- Si es un saludo simple, responde amablemente y menciona que puedes ayudar con preguntas sobre los documentos.
- Si la pregunta NO está relacionada con los documentos (temas externos como Pokémon, deportes, clima, etc.), rechaza educadamente y redirige al usuario a preguntar sobre los documentos.
- Si la pregunta SÍ está relacionada con los documentos, responde basándote en el contexto y cita las fuentes.
- No cites documentos si no usaste información de ellos en tu respuesta."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self.generate_chat_completion(messages, temperature=temperature)
