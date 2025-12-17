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
    <div className="relative flex flex-col h-full">
      {/* Results area */}
      <div className="flex-1 overflow-y-auto p-6 pb-24 space-y-4 bg-dark-800 custom-scrollbar">
        {isLoading && <Spinner text="Buscando" />}

        {error && (
          <div className="bg-red-900/50 text-red-300 p-4 rounded-lg border border-red-700">
            <p className="font-medium">Error</p>
            <p className="text-sm">{error}</p>
          </div>
        )}

        {!isLoading && !error && !results && (
          <div className="flex flex-col items-center justify-center h-full text-dark-200">
            <div className="w-16 h-16 bg-dark-600 rounded-full flex items-center justify-center mb-4">
              <Search className="w-8 h-8 text-dark-100" />
            </div>
            <p className="text-center text-dark-50 font-medium">
              Busca fragmentos relevantes en tus documentos
            </p>
            <p className="text-sm text-dark-200 mt-1">
              Los resultados mostrarán el contenido y la fuente
            </p>
          </div>
        )}

        {results && results.results.length === 0 && (
          <div className="text-center py-8 text-dark-200">
            <p>No se encontraron resultados para "{results.query}"</p>
          </div>
        )}

        {results && results.results.length > 0 && (
          <div className="space-y-4">
            <p className="text-sm text-dark-100">
              {results.total_results} resultado{results.total_results !== 1 ? 's' : ''} para "{results.query}"
            </p>

            {results.results.map((result, index) => (
              <div
                key={index}
                className="bg-dark-600 rounded-xl border border-dark-400 p-4 
                           hover:bg-dark-500 transition-all duration-200"
              >
                {/* Header */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2 text-primary-400 font-medium">
                    <FileText className="w-4 h-4" />
                    {result.document_name}
                  </div>
                  <span className="bg-primary-900/50 text-primary-300 px-3 py-1 rounded-full text-xs font-medium">
                    {(result.score * 100).toFixed(1)}% relevante
                  </span>
                </div>

                {/* Content */}
                <p className="text-dark-100 text-sm leading-relaxed mb-3">
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
                    className="inline-flex items-center gap-1 text-sm text-primary-400 hover:text-primary-300 hover:underline"
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

      {/* Search input - floating at bottom with gradient fade */}
      <div className="absolute bottom-0 left-0 right-0 pointer-events-none">
        <div className="h-16 bg-gradient-to-t from-dark-800 to-transparent" />
      </div>
      <form onSubmit={handleSearch} className="absolute bottom-0 left-0 right-0 px-6 pb-6 pt-4">
        <div className="flex gap-3 max-w-3xl mx-auto">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-200" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Buscar en documentos..."
              disabled={isLoading}
              className="w-full pl-12 pr-4 py-3 bg-dark-600 border border-dark-400 rounded-full 
                         focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
                         disabled:bg-dark-700 disabled:cursor-not-allowed
                         transition-all text-dark-50 placeholder-dark-200"
            />
          </div>
          <button
            type="submit"
            disabled={isLoading || !query.trim()}
            className="px-6 py-3 bg-primary-600 text-white rounded-full font-medium
                       hover:bg-primary-500 disabled:bg-dark-400 disabled:cursor-not-allowed
                       transition-all duration-200 hover:shadow-md"
          >
            Buscar
          </button>
        </div>
      </form>
    </div>
  );
}
