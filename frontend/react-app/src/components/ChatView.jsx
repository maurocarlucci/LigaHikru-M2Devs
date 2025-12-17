import { useState, useRef, useEffect } from 'react';
import { Send, FileText } from 'lucide-react';
import { askQuestion } from '../services/api';
import Spinner from './Spinner';

/**
 * Formats text with markdown-style bold (**text**) to HTML <strong> tags
 * Also escapes HTML to prevent XSS
 */
function formatBoldText(text) {
  if (!text) return '';
  // Escape HTML first to prevent XSS
  const escaped = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
  // Convert **text** to <strong>text</strong>
  return escaped.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
}

/**
 * Groups citations by document name and collects all page numbers
 * Returns array of { document_name, pages: [1, 3, 4], avgScore }
 */
function groupCitations(citations) {
  if (!citations || citations.length === 0) return [];
  
  const grouped = {};
  citations.forEach((cit) => {
    const name = cit.document_name;
    if (!grouped[name]) {
      grouped[name] = {
        document_name: name,
        pages: [],
        scores: [],
        source_url: cit.source_url,
      };
    }
    if (cit.page_number && !grouped[name].pages.includes(cit.page_number)) {
      grouped[name].pages.push(cit.page_number);
    }
    grouped[name].scores.push(cit.score);
  });

  // Convert to array and calculate average score
  return Object.values(grouped).map((g) => ({
    ...g,
    pages: g.pages.sort((a, b) => a - b),
    avgScore: g.scores.reduce((a, b) => a + b, 0) / g.scores.length,
  }));
}

/**
 * Chat View Component
 * Flow 1: Ask questions and receive AI-generated answers with citations
 */
export default function ChatView() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const question = input.trim();
    if (!question || isLoading) return;

    // Add user message
    setMessages((prev) => [...prev, { role: 'user', content: question }]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await askQuestion(question);
      
      // Add assistant message with citations
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: response.answer,
          citations: response.citations || [],
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Error: ${error.message}`,
          isError: true,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 custom-scrollbar">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <FileText className="w-12 h-12 mb-3" />
            <p className="text-center">
              Haz una pregunta sobre tus documentos
              <br />
              <span className="text-sm">La IA buscará en tu base de conocimiento</span>
            </p>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`animate-fade-in ${
              message.role === 'user' ? 'flex justify-end' : 'flex justify-start'
            }`}
          >
            <div
              className={`max-w-[75%] rounded-2xl px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-primary-500 text-white'
                  : message.isError
                  ? 'bg-red-50 text-red-700 border border-red-200'
                  : 'bg-white text-gray-800 border border-gray-200 shadow-sm'
              }`}
            >
              <p className="whitespace-pre-wrap" dangerouslySetInnerHTML={{ __html: formatBoldText(message.content) }} />

              {/* Citations - grouped by document */}
              {message.citations && message.citations.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <p className="text-xs font-semibold text-gray-500 mb-2">Fuentes:</p>
                  <div className="space-y-2">
                    {groupCitations(message.citations).map((group, citIndex) => (
                      <div
                        key={citIndex}
                        className="text-xs bg-gray-50 rounded-lg p-2 border-l-3 border-primary-400"
                      >
                        <div className="flex items-center gap-2 text-primary-600 font-medium">
                          <FileText className="w-3 h-3" />
                          {group.document_name}
                        </div>
                        <div className="text-gray-500 mt-1">
                          {group.pages.length > 0 && (
                            <span>
                              {group.pages.length === 1 
                                ? `Página ${group.pages[0]}` 
                                : `Páginas ${group.pages.join(', ')}`}
                              {' • '}
                            </span>
                          )}
                          Relevancia: {(group.avgScore * 100).toFixed(1)}%
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white rounded-2xl px-6 py-5 border border-gray-200 shadow-sm min-w-[200px]">
              <Spinner text="Pensando..." />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <form onSubmit={handleSubmit} className="p-4 bg-white border-t border-gray-200">
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Haz una pregunta sobre los documentos..."
            disabled={isLoading}
            className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-full 
                       focus:outline-none focus:border-primary-400 
                       disabled:bg-gray-50 disabled:cursor-not-allowed
                       transition-colors"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-6 py-3 bg-primary-500 text-white rounded-full font-medium
                       hover:bg-primary-600 disabled:bg-gray-300 disabled:cursor-not-allowed
                       transition-all duration-200 hover:shadow-lg hover:-translate-y-0.5
                       flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
            Enviar
          </button>
        </div>
      </form>
    </div>
  );
}
