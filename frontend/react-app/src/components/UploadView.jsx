import { useState, useRef, useEffect } from 'react';
import { Upload, FileText, Trash2, Plus, X, CheckCircle, XCircle } from 'lucide-react';
import { uploadDocument, listDocuments, deleteDocument } from '../services/api';
import Spinner from './Spinner';

/**
 * Document Manager View Component
 * Manages documents: list, upload, and delete with table layout and modal
 */
export default function UploadView() {
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [deletingFile, setDeletingFile] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const [notification, setNotification] = useState(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    setIsLoading(true);
    try {
      const response = await listDocuments();
      setDocuments(response.documents || []);
    } catch (error) {
      showNotification('error', `Error cargando documentos: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const showNotification = (type, message) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 5000);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) handleUpload(file);
  };

  const handleUpload = async (file) => {
    const validExtensions = ['.pdf', '.txt', '.md'];
    const ext = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    
    if (!validExtensions.includes(ext)) {
      showNotification('error', `Formato no soportado: ${ext}. Use PDF, TXT o MD`);
      return;
    }

    setIsUploading(true);

    try {
      const response = await uploadDocument(file);
      showNotification('success', `${response.filename} procesado (${response.chunks_processed} chunks)`);
      setShowUploadModal(false);
      loadDocuments();
    } catch (error) {
      showNotification('error', error.message);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDeleteClick = (filename) => {
    setDeleteConfirm(filename);
  };

  const handleDeleteConfirm = async () => {
    const filename = deleteConfirm;
    setDeleteConfirm(null);
    setDeletingFile(filename);

    try {
      await deleteDocument(filename);
      showNotification('success', `${filename} eliminado`);
      loadDocuments();
    } catch (error) {
      showNotification('error', `Error eliminando: ${error.message}`);
    } finally {
      setDeletingFile(null);
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '-';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="flex flex-col h-full bg-dark-800 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-dark-50">Gestor de Documentos</h2>
          <p className="text-sm text-dark-200 mt-1">
            Administra los documentos de tu base de conocimiento
          </p>
        </div>
        <button
          onClick={() => setShowUploadModal(true)}
          className="flex items-center gap-2 px-4 py-2.5 bg-primary-600 text-white rounded-lg font-medium
                     hover:bg-primary-500 transition-colors shadow-lg shadow-primary-900/30"
        >
          <Plus className="w-4 h-4" />
          Añadir documento
        </button>
      </div>

      {/* Notification */}
      {notification && (
        <div
          className={`p-3 rounded-lg mb-4 flex items-center gap-2 animate-fade-in ${
            notification.type === 'success'
              ? 'bg-green-900/30 border border-green-700 text-green-300'
              : 'bg-red-900/30 border border-red-700 text-red-300'
          }`}
        >
          {notification.type === 'success' ? (
            <CheckCircle className="w-4 h-4 flex-shrink-0" />
          ) : (
            <XCircle className="w-4 h-4 flex-shrink-0" />
          )}
          <span className="text-sm">{notification.message}</span>
        </div>
      )}

      {/* Table */}
      <div className="flex-1 overflow-hidden rounded-xl border border-dark-400 bg-dark-700">
        {/* Table Header */}
        <div className="grid grid-cols-12 gap-4 px-4 py-3 bg-dark-600 border-b border-dark-400 text-xs font-medium text-dark-100 uppercase tracking-wider">
          <div className="col-span-6">Nombre</div>
          <div className="col-span-2">Tamaño</div>
          <div className="col-span-3">Fecha</div>
          <div className="col-span-1"></div>
        </div>

        {/* Table Body */}
        <div className="overflow-y-auto custom-scrollbar" style={{ maxHeight: 'calc(100% - 44px)' }}>
          {isLoading ? (
            <div className="flex items-center justify-center py-16">
              <Spinner text="Cargando documentos" />
            </div>
          ) : documents.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-dark-200">
              <FileText className="w-12 h-12 mb-4 text-dark-400" />
              <p className="text-dark-100 font-medium">No hay documentos</p>
              <p className="text-sm mt-1">Haz clic en "Añadir documento" para comenzar</p>
            </div>
          ) : (
            documents.map((doc, index) => (
              <div
                key={index}
                className="grid grid-cols-12 gap-4 px-4 py-3 border-b border-dark-500 hover:bg-dark-600 transition-colors items-center group"
              >
                <div className="col-span-6 flex items-center gap-3 min-w-0">
                  <FileText className="w-5 h-5 text-primary-400 flex-shrink-0" />
                  <span className="text-dark-50 truncate">{doc.name}</span>
                </div>
                <div className="col-span-2 text-dark-200 text-sm">
                  {formatFileSize(doc.size)}
                </div>
                <div className="col-span-3 text-dark-200 text-sm">
                  {formatDate(doc.last_modified)}
                </div>
                <div className="col-span-1 flex justify-end">
                  <button
                    onClick={() => handleDeleteClick(doc.name)}
                    disabled={deletingFile === doc.name}
                    className="p-1.5 text-dark-300 hover:text-red-400 hover:bg-red-900/30 rounded-lg 
                               transition-all disabled:opacity-50"
                    title="Eliminar"
                  >
                    {deletingFile === doc.name ? (
                      <div className="w-4 h-4 border-2 border-dark-300 border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <Trash2 className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Footer info */}
      <div className="mt-4 text-sm text-dark-300">
        {documents.length} documento{documents.length !== 1 ? 's' : ''} en total
      </div>

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-dark-700 rounded-2xl border border-dark-400 shadow-2xl w-full max-w-md mx-4 animate-fade-in">
            <div className="p-6">
              <div className="w-12 h-12 bg-red-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                <Trash2 className="w-6 h-6 text-red-400" />
              </div>
              <h3 className="text-lg font-semibold text-dark-50 text-center mb-2">
                Eliminar documento
              </h3>
              <p className="text-dark-200 text-center text-sm">
                ¿Estás seguro de que deseas eliminar <span className="text-dark-50 font-medium">"{deleteConfirm}"</span>?
              </p>
              <p className="text-dark-300 text-center text-xs mt-2">
                Esta acción no se puede deshacer.
              </p>
            </div>
            <div className="px-6 py-4 border-t border-dark-400 flex gap-3 justify-end">
              <button
                onClick={() => setDeleteConfirm(null)}
                className="px-4 py-2 text-dark-100 hover:text-dark-50 hover:bg-dark-500 rounded-lg transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleDeleteConfirm}
                className="px-4 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-500 transition-colors"
              >
                Eliminar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-dark-700 rounded-2xl border border-dark-400 shadow-2xl w-full max-w-lg mx-4 animate-fade-in">
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-dark-400">
              <h3 className="text-lg font-semibold text-dark-50">Añadir documento</h3>
              <button
                onClick={() => !isUploading && setShowUploadModal(false)}
                disabled={isUploading}
                className="p-1 text-dark-200 hover:text-dark-50 hover:bg-dark-500 rounded-lg transition-colors disabled:opacity-50"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6">
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => !isUploading && fileInputRef.current?.click()}
                className={`
                  border-2 border-dashed rounded-xl p-12 cursor-pointer transition-all duration-200
                  flex flex-col items-center justify-center
                  ${isDragging 
                    ? 'border-primary-500 bg-primary-900/20' 
                    : 'border-dark-400 hover:border-primary-400 hover:bg-dark-600'
                  }
                  ${isUploading ? 'pointer-events-none' : ''}
                `}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.txt,.md"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                {isUploading ? (
                  <Spinner text="Procesando documento" />
                ) : (
                  <>
                    <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-4 ${isDragging ? 'bg-primary-900/50' : 'bg-dark-500'}`}>
                      <Upload className={`w-8 h-8 ${isDragging ? 'text-primary-400' : 'text-dark-200'}`} />
                    </div>
                    <p className="text-dark-50 font-medium text-center">
                      Arrastra un archivo aquí
                    </p>
                    <p className="text-dark-200 text-sm mt-1">
                      o haz clic para seleccionar
                    </p>
                    <p className="text-dark-300 text-xs mt-4">
                      Formatos soportados: PDF, TXT, MD
                    </p>
                  </>
                )}
              </div>
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-4 border-t border-dark-400 flex justify-end">
              <button
                onClick={() => setShowUploadModal(false)}
                disabled={isUploading}
                className="px-4 py-2 text-dark-100 hover:text-dark-50 hover:bg-dark-500 rounded-lg transition-colors disabled:opacity-50"
              >
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
