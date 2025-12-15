import PyPDF2
import io
from typing import List, Optional
import re
from app.models.schemas import DocumentChunk
from app.services.azure_openai_service import AzureOpenAIService
from app.services.azure_search_service import AzureSearchService
from app.services.azure_blob_service import AzureBlobService


class DocumentProcessor:
    """Procesa documentos: chunking, embeddings e indexación"""
    
    def __init__(self):
        self.openai_service = AzureOpenAIService()
        self.search_service = AzureSearchService()
        self.blob_service = AzureBlobService()
        self.chunk_size = 1000  # caracteres por chunk
        self.chunk_overlap = 200  # overlap entre chunks
    
    def process_pdf(self, file_content: bytes, filename: str) -> List[DocumentChunk]:
        """Procesa un PDF y lo divide en chunks"""
        chunks = []
        
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            if len(pdf_reader.pages) == 0:
                raise Exception("El PDF no tiene páginas")
            
            full_text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        full_text += f"\n\n--- Página {page_num + 1} ---\n\n{page_text}"
                except Exception as e:
                    print(f"Advertencia: No se pudo extraer texto de la página {page_num + 1}: {str(e)}")
                    continue
            
            if not full_text or not full_text.strip():
                raise Exception("No se pudo extraer texto del PDF. El PDF puede ser una imagen escaneada o estar protegido.")
            
            # Dividir en chunks
            text_chunks = self._split_text(full_text)
            
            if not text_chunks:
                raise Exception("No se generaron chunks del texto extraído")
            
            for idx, chunk_text in enumerate(text_chunks):
                if not chunk_text or not chunk_text.strip():
                    continue  # Saltar chunks vacíos
                    
                # Determinar página aproximada
                page_num = self._estimate_page_number(chunk_text, len(pdf_reader.pages))
                
                chunks.append(DocumentChunk(
                    content=chunk_text,
                    source=filename,
                    page_number=page_num,
                    chunk_index=idx,
                    metadata={"total_pages": len(pdf_reader.pages)}
                ))
            
            if not chunks:
                raise Exception("No se generaron chunks válidos del PDF")
            
            return chunks
        
        except Exception as e:
            raise Exception(f"Error procesando PDF: {str(e)}")
    
    def process_text(self, text: str, filename: str) -> List[DocumentChunk]:
        """Procesa un texto plano y lo divide en chunks"""
        chunks = []
        text_chunks = self._split_text(text)
        
        for idx, chunk_text in enumerate(text_chunks):
            chunks.append(DocumentChunk(
                content=chunk_text,
                source=filename,
                chunk_index=idx
            ))
        
        return chunks
    
    def _split_text(self, text: str) -> List[str]:
        """Divide texto en chunks con overlap"""
        # Limpiar texto
        text = re.sub(r'\s+', ' ', text).strip()
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Intentar cortar en un punto natural (punto, salto de línea, etc.)
            cut_point = end
            for delimiter in ['. ', '\n', '; ', '! ', '? ']:
                last_delim = text.rfind(delimiter, start, end)
                if last_delim > start:
                    cut_point = last_delim + len(delimiter)
                    break
            
            chunks.append(text[start:cut_point].strip())
            start = cut_point - self.chunk_overlap
        
        return chunks
    
    def _estimate_page_number(self, chunk_text: str, total_pages: int) -> Optional[int]:
        """Estima el número de página basado en marcadores en el texto"""
        # Buscar patrones como "--- Página X ---"
        match = re.search(r'--- Página (\d+) ---', chunk_text)
        if match:
            return int(match.group(1))
        return None
    
    def index_document(self, chunks: List[DocumentChunk]) -> int:
        """Indexa chunks en Azure AI Search con embeddings"""
        if not chunks:
            return 0
        
        # Generar embeddings para todos los chunks
        chunk_texts = [chunk.content for chunk in chunks]
        try:
            embeddings = self.openai_service.generate_embeddings(chunk_texts)
        except Exception as e:
            raise Exception(f"Error generando embeddings: {str(e)}")
        
        # Verificar dimensiones del embedding
        if embeddings and len(embeddings) > 0:
            embedding_dim = len(embeddings[0])
            if embedding_dim != 1536:
                raise Exception(f"Dimensiones incorrectas del embedding: {embedding_dim}. Se esperan 1536 dimensiones.")
        
        # Subir cada chunk al índice
        indexed = 0
        errors = []
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            try:
                source_url = self.blob_service.get_file_url(chunk.source)
                self.search_service.upload_document_chunk(
                    document_name=chunk.source,
                    content=chunk.content,
                    content_vector=embedding,
                    chunk_index=chunk.chunk_index,
                    page_number=chunk.page_number,
                    source_url=source_url,
                    metadata=chunk.metadata
                )
                indexed += 1
            except Exception as e:
                error_msg = str(e)
                errors.append(f"Chunk {chunk.chunk_index}: {error_msg}")
                print(f"Error indexando chunk {chunk.chunk_index}: {error_msg}")
                continue
        
        if indexed == 0 and errors:
            # Si ningún chunk se indexó, lanzar el primer error
            raise Exception(f"No se pudieron indexar los chunks. Primer error: {errors[0]}")
        
        return indexed
