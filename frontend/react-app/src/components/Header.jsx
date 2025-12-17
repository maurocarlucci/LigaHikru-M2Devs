import { Sparkles } from 'lucide-react';

/**
 * Header component with app branding
 * Displays the app title and description
 */
export default function Header() {
  return (
    <header className="bg-dark-700 border-b border-dark-400 px-6 py-4">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-lg font-semibold text-dark-50">Hikru Insight</h1>
          <p className="text-sm text-dark-100">
            Asistente inteligente de documentos
          </p>
        </div>
      </div>
    </header>
  );
}
