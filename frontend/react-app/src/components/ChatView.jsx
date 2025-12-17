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
    if (messages.length > 0) {
      scrollToBottom();
    }
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
    <div className="relative flex flex-col h-full">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-6 pb-24 space-y-4 bg-dark-800 custom-scrollbar">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-dark-200">
            <div className="w-16 h-16 bg-dark-600 rounded-full flex items-center justify-center mb-4">
              <FileText className="w-8 h-8 text-dark-100" />
            </div>
            <p className="text-center text-dark-50 font-medium">
              Haz una pregunta sobre tus documentos
            </p>
            <p className="text-sm text-dark-200 mt-1">
              La IA buscará en tu base de conocimiento
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
              className={`max-w-[70%] rounded-2xl px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-primary-600 text-white message-tail-user'
                  : message.isError
                  ? 'bg-red-900/50 text-red-300 border border-red-700'
                  : 'bg-dark-500 text-dark-50 message-tail-assistant'
              }`}
            >
              <p className="whitespace-pre-wrap leading-relaxed" dangerouslySetInnerHTML={{ __html: formatBoldText(message.content) }} />

              {/* Citations - grouped by document */}
              {message.citations && message.citations.length > 0 && (
                <div className="mt-3 pt-3 border-t border-dark-400">
                  <p className="text-xs font-semibold text-dark-100 mb-2">Fuentes:</p>
                  <div className="space-y-2">
                    {groupCitations(message.citations).map((group, citIndex) => (
                      <div
                        key={citIndex}
                        className="text-xs bg-dark-600 rounded-lg p-2 border-l-2 border-primary-500"
                      >
                        <div className="flex items-center gap-2 text-primary-400 font-medium">
                          <FileText className="w-3 h-3" />
                          {group.document_name}
                        </div>
                        <div className="text-dark-100 mt-1">
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
          <div className="flex justify-start animate-fade-in">
            <div className="bg-dark-500 rounded-2xl px-5 py-4 message-tail-assistant">
              <Spinner text="Pensando" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area - floating at bottom with gradient fade */}
      <div className="absolute bottom-0 left-0 right-0 pointer-events-none">
        <div className="h-16 bg-gradient-to-t from-dark-800 to-transparent" />
      </div>
      <form onSubmit={handleSubmit} className="absolute bottom-0 left-0 right-0 px-6 pb-6 pt-4">
        <div className="flex gap-3 max-w-3xl mx-auto">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Escribe tu pregunta aquí..."
            disabled={isLoading}
            className="flex-1 px-5 py-3 bg-dark-600 border border-dark-400 rounded-full 
                       focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
                       disabled:bg-dark-700 disabled:cursor-not-allowed
                       transition-all text-dark-50 placeholder-dark-200"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-6 py-3 bg-primary-600 text-white rounded-full font-medium
                       hover:bg-primary-500 disabled:bg-dark-400 disabled:cursor-not-allowed
                       transition-all duration-200 hover:shadow-md
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
