import { useState } from 'react';
import { Search, FileText, ExternalLink } from 'lucide-react';
import { searchDocuments } from '../services/api';
import Spinner from './Spinner';

/**
 * Search View Component
 * Flow 2: Search documents and display relevant fragments with source info
 */
export default function SearchView() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    const searchQuery = query.trim();
    if (!searchQuery || isLoading) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await searchDocuments(searchQuery);
      setResults(response);
    } catch (err) {
      setError(err.message);
      setResults(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Results area */}
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50 custom-scrollbar">
        {isLoading && <Spinner text="Buscando..." />}

        {error && (
          <div className="bg-red-50 text-red-700 p-4 rounded-lg border border-red-200">
            <p className="font-medium">Error</p>
            <p className="text-sm">{error}</p>
          </div>
        )}

        {!isLoading && !error && !results && (
          <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <Search className="w-12 h-12 mb-3" />
            <p className="text-center">
              Busca fragmentos relevantes en tus documentos
              <br />
              <span className="text-sm">Los resultados mostrarán el contenido y la fuente</span>
            </p>
          </div>
        )}

        {results && results.results.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <p>No se encontraron resultados para "{results.query}"</p>
          </div>
        )}

        {results && results.results.length > 0 && (
          <div className="space-y-4">
            <p className="text-sm text-gray-500">
              {results.total_results} resultado{results.total_results !== 1 ? 's' : ''} para "{results.query}"
            </p>

            {results.results.map((result, index) => (
              <div
                key={index}
                className="bg-white rounded-xl border border-gray-200 p-4 
                           hover:shadow-md hover:-translate-y-0.5 transition-all duration-200"
              >
                {/* Header */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2 text-primary-600 font-medium">
                    <FileText className="w-4 h-4" />
                    {result.document_name}
                  </div>
                  <span className="bg-primary-100 text-primary-700 px-3 py-1 rounded-full text-xs font-medium">
                    {(result.score * 100).toFixed(1)}% relevante
                  </span>
                </div>

                {/* Content */}
                <p className="text-gray-600 text-sm leading-relaxed mb-3">
                  {result.content.length > 400
                    ? `${result.content.substring(0, 400)}...`
                    : result.content}
                </p>

                {/* Link */}
                {result.source_url && (
                  <a
                    href={result.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-sm text-primary-600 hover:text-primary-700 hover:underline"
                  >
                    Ver documento
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Search input - at bottom like ChatView */}
      <form onSubmit={handleSearch} className="p-4 bg-white border-t border-gray-200">
        <div className="flex gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Buscar en documentos..."
              disabled={isLoading}
              className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-full 
                         focus:outline-none focus:border-primary-400 
                         disabled:bg-gray-50 disabled:cursor-not-allowed
                         transition-colors"
            />
          </div>
          <button
            type="submit"
            disabled={isLoading || !query.trim()}
            className="px-6 py-3 bg-primary-500 text-white rounded-full font-medium
                       hover:bg-primary-600 disabled:bg-gray-300 disabled:cursor-not-allowed
                       transition-all duration-200 hover:shadow-lg hover:-translate-y-0.5"
          >
            Buscar
          </button>
        </div>
      </form>
    </div>
  );
}
