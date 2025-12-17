import { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle, XCircle } from 'lucide-react';
import { uploadDocument } from '../services/api';
import Spinner from './Spinner';

/**
 * Upload View Component
 * Flow 3: Upload documents (PDF, TXT, MD) to be processed and indexed
 */
export default function UploadView() {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const fileInputRef = useRef(null);

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
    // Validate file type
    const validExtensions = ['.pdf', '.txt', '.md'];
    const ext = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    
    if (!validExtensions.includes(ext)) {
      setUploadResult({
        success: false,
        message: `Formato no soportado: ${ext}. Use PDF, TXT o MD`,
      });
      return;
    }

    setIsUploading(true);
    setUploadResult(null);

    try {
      const response = await uploadDocument(file);
      setUploadResult({
        success: true,
        message: response.message,
        filename: response.filename,
        chunks: response.chunks_processed,
      });
    } catch (error) {
      setUploadResult({
        success: false,
        message: error.message,
      });
    } finally {
      setIsUploading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const resetUpload = () => {
    setUploadResult(null);
  };

  return (
    <div className="flex flex-col h-full p-4">
      {/* Upload area */}
      <div
        onClick={() => !isUploading && fileInputRef.current?.click()}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          flex flex-col items-center justify-center
          border-2 border-dashed rounded-xl p-10 cursor-pointer
          transition-all duration-200
          ${isDragging 
            ? 'border-primary-500 bg-primary-50' 
            : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
          }
          ${isUploading ? 'pointer-events-none opacity-60' : ''}
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
          <Spinner text="Subiendo y procesando documento..." />
        ) : (
          <>
            <Upload className={`w-12 h-12 mb-4 ${isDragging ? 'text-primary-500' : 'text-gray-400'}`} />
            <p className="text-gray-700 font-medium mb-2">
              Arrastra un archivo aquí o haz clic para seleccionar
            </p>
            <p className="text-sm text-gray-500">
              Soporta PDF, TXT, MD
            </p>
          </>
        )}
      </div>

      {/* Upload result */}
      {uploadResult && (
        <div
          className={`mt-4 p-4 rounded-xl animate-fade-in ${
            uploadResult.success
              ? 'bg-green-50 border border-green-200'
              : 'bg-red-50 border border-red-200'
          }`}
        >
          <div className="flex items-start gap-3">
            {uploadResult.success ? (
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            ) : (
              <XCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            )}
            <div className="flex-1">
              <p className={`font-medium ${uploadResult.success ? 'text-green-800' : 'text-red-800'}`}>
                {uploadResult.success ? 'Documento procesado' : 'Error'}
              </p>
              <p className={`text-sm mt-1 ${uploadResult.success ? 'text-green-700' : 'text-red-700'}`}>
                {uploadResult.message}
              </p>
              {uploadResult.success && (
                <div className="mt-2 text-sm text-green-600">
                  <p className="flex items-center gap-2">
                    <FileText className="w-4 h-4" />
                    {uploadResult.filename}
                  </p>
                  <p className="mt-1">
                    {uploadResult.chunks} chunks procesados e indexados
                  </p>
                </div>
              )}
            </div>
          </div>

          <button
            onClick={resetUpload}
            className="mt-3 text-sm text-gray-600 hover:text-gray-800 underline"
          >
            Subir otro documento
          </button>
        </div>
      )}

      {/* Instructions */}
      <div className="mt-auto pt-4">
        <div className="bg-blue-50 rounded-xl p-4 border border-blue-100">
          <h3 className="font-medium text-blue-800 mb-2">Información</h3>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• Los documentos se procesan y dividen en fragmentos</li>
            <li>• Se generan embeddings para búsqueda semántica</li>
            <li>• El contenido queda disponible para consultas de IA</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
