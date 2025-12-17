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
        self.chunk_size = 700  # caracteres por chunk (reduced for better context)
        self.chunk_overlap = 150  # overlap entre chunks
    
    def process_pdf(self, file_content: bytes, filename: str) -> List[DocumentChunk]:
        """Procesa un PDF y lo divide en chunks, preservando estructura y metadata de página"""
        chunks = []
        
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            if len(pdf_reader.pages) == 0:
                raise Exception("El PDF no tiene páginas")
            
            # Extract text per page with metadata
            pages_data = []
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        pages_data.append({
                            "page_number": page_num + 1,
                            "text": page_text
                        })
                except Exception as e:
                    print(f"Advertencia: No se pudo extraer texto de la página {page_num + 1}: {str(e)}")
                    continue
            
            if not pages_data:
                raise Exception("No se pudo extraer texto del PDF. El PDF puede ser una imagen escaneada o estar protegido.")
            
            # Process each page and create chunks with accurate page numbers
            chunk_idx = 0
            for page_data in pages_data:
                page_text = page_data["text"]
                page_number = page_data["page_number"]
                
                # Split this page's text into chunks
                page_chunks = self._split_text(page_text)
                
                for chunk_text in page_chunks:
                    if not chunk_text or not chunk_text.strip():
                        continue
                    
                    chunks.append(DocumentChunk(
                        content=chunk_text,
                        source=filename,
                        page_number=page_number,
                        chunk_index=chunk_idx,
                        metadata={"total_pages": len(pdf_reader.pages)}
                    ))
                    chunk_idx += 1
            
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
    
    def _is_section_header(self, line: str) -> bool:
        """Detect if a line looks like a section header"""
        line = line.strip()
        if not line or len(line) > 100:
            return False
        # Numbered sections: "1.", "1.1", "7. CRITERIOS"
        if re.match(r'^\d+\.(\d+\.?)?\s+[A-ZÁÉÍÓÚÑ]', line):
            return True
        # ALL CAPS headers
        if line.isupper() and len(line) > 3:
            return True
        # Roman numerals: "I.", "II.", "III."
        if re.match(r'^[IVXLC]+\.\s+', line):
            return True
        return False
    
    def _split_text(self, text: str) -> List[str]:
        """Divide texto en chunks con overlap, preservando estructura y respetando secciones"""
        # Clean text while preserving structure
        text = re.sub(r'[^\S\n]+', ' ', text)  # Multiple spaces -> single space (preserve \n)
        text = re.sub(r'\n{3,}', '\n\n', text)  # 3+ newlines -> 2 newlines
        text = text.strip()
        
        if not text:
            return []
        
        if len(text) <= self.chunk_size:
            return [text]
        
        # First pass: split by section headers if present
        lines = text.split('\n')
        sections = []
        current_section = []
        
        for line in lines:
            if self._is_section_header(line) and current_section:
                # Save previous section and start new one
                sections.append('\n'.join(current_section))
                current_section = [line]
            else:
                current_section.append(line)
        
        if current_section:
            sections.append('\n'.join(current_section))
        
        # If no sections found, treat entire text as one section
        if len(sections) <= 1:
            sections = [text]
        
        # Second pass: split large sections into chunks
        chunks = []
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            if len(section) <= self.chunk_size:
                chunks.append(section)
            else:
                # Recursively split large sections
                section_chunks = self._split_large_section(section)
                chunks.extend(section_chunks)
        
        return chunks
    
    def _split_large_section(self, text: str) -> List[str]:
        """Split a large section into chunks, respecting paragraph and sentence boundaries"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            if end >= len(text):
                remaining = text[start:].strip()
                if remaining:
                    chunks.append(remaining)
                break
            
            chunk_text = text[start:end]
            cut_point = end
            
            # Priority 1: Double newline (paragraph break)
            para_break = chunk_text.rfind('\n\n')
            if para_break > len(chunk_text) * 0.3:
                cut_point = start + para_break + 2
            else:
                # Priority 2: Single newline (but not mid-list)
                line_break = chunk_text.rfind('\n')
                if line_break > len(chunk_text) * 0.4:
                    # Check if next line is a list item - if so, keep together
                    next_char_idx = start + line_break + 1
                    if next_char_idx < len(text):
                        next_line_start = text[next_char_idx:next_char_idx+5]
                        if not re.match(r'^[•\-\*]\s|^\d+[\.\)]\s', next_line_start):
                            cut_point = start + line_break + 1
                        else:
                            # Try to find a break before the list
                            earlier_break = chunk_text[:line_break].rfind('\n')
                            if earlier_break > len(chunk_text) * 0.3:
                                cut_point = start + earlier_break + 1
                else:
                    # Priority 3: Sentence end
                    for delimiter in ['. ', '! ', '? ', '; ']:
                        last_delim = chunk_text.rfind(delimiter)
                        if last_delim > len(chunk_text) * 0.5:
                            cut_point = start + last_delim + len(delimiter)
                            break
            
            chunk_content = text[start:cut_point].strip()
            if chunk_content:
                chunks.append(chunk_content)
            
            new_start = cut_point - self.chunk_overlap
            start = max(new_start, start + 1)
        
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
