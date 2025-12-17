/**
 * API Service Layer
 * Handles all communication with the backend REST API
 * Base URL is configured via environment variable VITE_API_BASE_URL
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

/**
 * Ask a question to the AI assistant
 * @param {string} question - The question to ask
 * @param {number} maxResults - Maximum number of document results to consider (default: 5)
 * @param {number} temperature - AI response creativity (0-1, default: 0.7)
 * @returns {Promise<{answer: string, citations: Array, sources: Array}>}
 */
export async function askQuestion(question, maxResults = 5, temperature = 0.7) {
  const response = await fetch(`${API_BASE}/chat/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      question,
      max_results: maxResults,
      temperature,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error de conexión' }));
    throw new Error(error.detail || 'Error al procesar la pregunta');
  }

  return response.json();
}

/**
 * Search documents for relevant fragments
 * @param {string} query - Search query
 * @param {number} maxResults - Maximum number of results (default: 10)
 * @returns {Promise<{results: Array, total_results: number, query: string}>}
 */
export async function searchDocuments(query, maxResults = 10) {
  const response = await fetch(`${API_BASE}/chat/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      max_results: maxResults,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error de conexión' }));
    throw new Error(error.detail || 'Error en la búsqueda');
  }

  return response.json();
}

/**
 * Upload a document to be processed and indexed
 * @param {File} file - The file to upload (PDF, TXT, or MD)
 * @returns {Promise<{filename: string, status: string, chunks_processed: number, message: string}>}
 */
export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error de conexión' }));
    throw new Error(error.detail || 'Error al subir el documento');
  }

  return response.json();
}

/**
 * List all documents in storage
 * @returns {Promise<{documents: Array, total: number}>}
 */
export async function listDocuments() {
  const response = await fetch(`${API_BASE}/documents/list`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error de conexión' }));
    throw new Error(error.detail || 'Error al listar documentos');
  }

  return response.json();
}

/**
 * Delete a document from storage
 * @param {string} filename - Name of the file to delete
 * @returns {Promise<{message: string}>}
 */
export async function deleteDocument(filename) {
  const response = await fetch(`${API_BASE}/documents/${encodeURIComponent(filename)}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error de conexión' }));
    throw new Error(error.detail || 'Error al eliminar documento');
  }

  return response.json();
}
