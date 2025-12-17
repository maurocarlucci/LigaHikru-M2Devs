import { BookOpen } from 'lucide-react';

/**
 * Header component with app branding
 * Displays the app title and description
 */
export default function Header() {
  return (
    <header className="bg-gradient-to-r from-primary-500 to-secondary-500 text-white px-6 py-5">
      <div className="flex items-center gap-3">
        <BookOpen className="w-8 h-8" />
        <div>
          <h1 className="text-xl font-semibold">LigaHikru - Documentos AI</h1>
          <p className="text-sm text-white/80">
            Consulta y busca información en tus documentos internos
          </p>
        </div>
      </div>
    </header>
  );
}
