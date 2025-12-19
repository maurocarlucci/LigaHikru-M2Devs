/**
 * API Service Layer
 * Handles all communication with the backend REST API
 * Base URL is configured via environment variable VITE_API_BASE_URL
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

/**
 * Get authentication token from localStorage
 */
function getAuthToken() {
  return localStorage.getItem('auth_token');
}

/**
 * Set authentication token in localStorage
 */
function setAuthToken(token) {
  localStorage.setItem('auth_token', token);
}

/**
 * Remove authentication token from localStorage
 */
function removeAuthToken() {
  localStorage.removeItem('auth_token');
}

/**
 * Get auth headers with token if available
 */
function getAuthHeaders() {
  const token = getAuthToken();
  const headers = {};
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
}

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
    headers: getAuthHeaders(),
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
  const response = await fetch(`${API_BASE}/documents/list`, {
    headers: getAuthHeaders(),
  });

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
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error de conexión' }));
    throw new Error(error.detail || 'Error al eliminar documento');
  }

  return response.json();
}

/**
 * Authentication functions
 */

/**
 * Sign up a new user
 * @param {string} email - User email
 * @param {string} username - Username
 * @param {string} password - Password
 * @returns {Promise<{access_token: string, token_type: string, user: object}>}
 */
export async function signUp(email, username, password) {
  const response = await fetch(`${API_BASE}/auth/signup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, username, password }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error de conexión' }));
    throw new Error(error.detail || 'Error al registrar usuario');
  }

  const data = await response.json();
  if (data.access_token) {
    setAuthToken(data.access_token);
  }
  return data;
}

/**
 * Login user
 * @param {string} email - User email
 * @param {string} password - Password
 * @returns {Promise<{access_token: string, token_type: string, user: object}>}
 */
export async function login(email, password) {
  const response = await fetch(`${API_BASE}/auth/login-json`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error de conexión' }));
    throw new Error(error.detail || 'Error al iniciar sesión');
  }

  const data = await response.json();
  if (data.access_token) {
    setAuthToken(data.access_token);
  }
  return data;
}

/**
 * Logout user
 */
export function logout() {
  removeAuthToken();
}

/**
 * Get current user from token
 */
export function getCurrentUser() {
  const token = getAuthToken();
  if (!token) return null;
  
  try {
    // Decode JWT token (simple base64 decode, no verification)
    const payload = JSON.parse(atob(token.split('.')[1]));
    return {
      id: payload.sub,
      email: payload.email,
      role: payload.role,
    };
  } catch (e) {
    return null;
  }
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated() {
  return !!getAuthToken();
}

// Export token management functions
export { getAuthToken, setAuthToken, removeAuthToken, getAuthHeaders };
