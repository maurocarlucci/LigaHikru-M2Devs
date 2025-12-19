import { Sparkles, LogOut, User, Crown } from 'lucide-react';

/**
 * Header component with app branding and user info
 * Displays the app title, description, and user menu
 */
export default function Header({ user, onLogout }) {
  return (
    <header className="bg-dark-700 border-b border-dark-400 px-6 py-4">
      <div className="flex items-center justify-between">
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

        {/* User Menu */}
        {user && (
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-dark-600 rounded-lg border border-dark-400">
              {user.role === 'admin' && (
                <Crown className="w-4 h-4 text-yellow-400" title="Administrador" />
              )}
              <User className="w-4 h-4 text-dark-300" />
              <span className="text-sm text-dark-100">{user.email}</span>
            </div>
            <button
              onClick={onLogout}
              className="flex items-center gap-2 px-3 py-1.5 text-dark-200 hover:text-dark-50 
                       hover:bg-dark-600 rounded-lg transition-colors border border-dark-400"
              title="Cerrar sesión"
            >
              <LogOut className="w-4 h-4" />
              <span className="text-sm">Salir</span>
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
