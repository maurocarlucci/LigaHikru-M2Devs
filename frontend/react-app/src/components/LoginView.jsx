import { useState } from 'react';
import { LogIn, Mail, Lock, User, Sparkles, AlertCircle, CheckCircle } from 'lucide-react';
import { login, signUp } from '../services/api';
import Spinner from './Spinner';

/**
 * Login/SignUp View Component
 * Handles user authentication with a toggle between login and signup
 */
export default function LoginView({ onLoginSuccess }) {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    // Validations
    if (!email || !password) {
      setError('Por favor completa todos los campos');
      return;
    }

    if (isSignUp) {
      if (!username) {
        setError('El username es requerido');
        return;
      }
      if (password.length < 6) {
        setError('La contraseña debe tener al menos 6 caracteres');
        return;
      }
      // Validar límite de 72 caracteres (límite de bcrypt)
      const passwordBytes = new TextEncoder().encode(password).length;
      if (passwordBytes > 72) {
        setError('La contraseña no puede tener más de 72 caracteres');
        return;
      }
      if (password !== confirmPassword) {
        setError('Las contraseñas no coinciden');
        return;
      }
    } else {
      // Validar también en login (aunque normalmente no debería ser necesario)
      const passwordBytes = new TextEncoder().encode(password).length;
      if (passwordBytes > 72) {
        setError('La contraseña no puede tener más de 72 caracteres');
        return;
      }
    }

    setIsLoading(true);

    try {
      if (isSignUp) {
        await signUp(email, username, password);
        setSuccess('¡Cuenta creada exitosamente! Redirigiendo...');
        setTimeout(() => {
          if (onLoginSuccess) onLoginSuccess();
        }, 1000);
      } else {
        await login(email, password);
        if (onLoginSuccess) onLoginSuccess();
      }
    } catch (err) {
      setError(err.message || 'Error al procesar la solicitud');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-screen bg-dark-800 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo/Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-600 rounded-2xl mb-4 shadow-lg shadow-primary-900/30">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-semibold text-dark-50 mb-2">Hikru Insight</h1>
          <p className="text-dark-200">
            {isSignUp ? 'Crea tu cuenta para comenzar' : 'Inicia sesión para continuar'}
          </p>
        </div>

        {/* Card */}
        <div className="bg-dark-700 rounded-2xl border border-dark-400 shadow-2xl p-8">
          {/* Toggle */}
          <div className="flex gap-2 mb-6 p-1 bg-dark-600 rounded-lg">
            <button
              onClick={() => {
                setIsSignUp(false);
                setError(null);
                setSuccess(null);
              }}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
                !isSignUp
                  ? 'bg-primary-600 text-white shadow-lg shadow-primary-900/30'
                  : 'text-dark-200 hover:text-dark-50'
              }`}
            >
              Iniciar Sesión
            </button>
            <button
              onClick={() => {
                setIsSignUp(true);
                setError(null);
                setSuccess(null);
              }}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
                isSignUp
                  ? 'bg-primary-600 text-white shadow-lg shadow-primary-900/30'
                  : 'text-dark-200 hover:text-dark-50'
              }`}
            >
              Registrarse
            </button>
          </div>

          {/* Error/Success Messages */}
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-900/30 border border-red-700 text-red-300 flex items-center gap-2 animate-fade-in">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span className="text-sm">{error}</span>
            </div>
          )}

          {success && (
            <div className="mb-4 p-3 rounded-lg bg-green-900/30 border border-green-700 text-green-300 flex items-center gap-2 animate-fade-in">
              <CheckCircle className="w-4 h-4 flex-shrink-0" />
              <span className="text-sm">{success}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {isSignUp && (
              <div>
                <label className="block text-sm font-medium text-dark-100 mb-2">
                  Username
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <User className="w-5 h-5 text-dark-300" />
                  </div>
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 bg-dark-600 border border-dark-400 rounded-lg text-dark-50 
                             placeholder-dark-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
                             transition-all"
                    placeholder="tu_usuario"
                    disabled={isLoading}
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-dark-100 mb-2">
                Email
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="w-5 h-5 text-dark-300" />
                </div>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-dark-600 border border-dark-400 rounded-lg text-dark-50 
                           placeholder-dark-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
                           transition-all"
                  placeholder="tu@email.com"
                  disabled={isLoading}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-dark-100 mb-2">
                Contraseña
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="w-5 h-5 text-dark-300" />
                </div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-dark-600 border border-dark-400 rounded-lg text-dark-50 
                           placeholder-dark-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
                           transition-all"
                  placeholder="••••••••"
                  disabled={isLoading}
                />
              </div>
            </div>

            {isSignUp && (
              <div>
                <label className="block text-sm font-medium text-dark-100 mb-2">
                  Confirmar Contraseña
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="w-5 h-5 text-dark-300" />
                  </div>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 bg-dark-600 border border-dark-400 rounded-lg text-dark-50 
                             placeholder-dark-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
                             transition-all"
                    placeholder="••••••••"
                    disabled={isLoading}
                  />
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-2.5 px-4 bg-primary-600 text-white rounded-lg font-medium
                       hover:bg-primary-500 transition-colors shadow-lg shadow-primary-900/30
                       disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>{isSignUp ? 'Creando cuenta...' : 'Iniciando sesión...'}</span>
                </>
              ) : (
                <>
                  <LogIn className="w-4 h-4" />
                  <span>{isSignUp ? 'Crear Cuenta' : 'Iniciar Sesión'}</span>
                </>
              )}
            </button>
          </form>

          {/* Footer */}
          <div className="mt-6 text-center">
            <p className="text-xs text-dark-300">
              {isSignUp ? (
                <>
                  ¿Ya tienes cuenta?{' '}
                  <button
                    onClick={() => {
                      setIsSignUp(false);
                      setError(null);
                    }}
                    className="text-primary-400 hover:text-primary-300 font-medium"
                  >
                    Inicia sesión
                  </button>
                </>
              ) : (
                <>
                  ¿No tienes cuenta?{' '}
                  <button
                    onClick={() => {
                      setIsSignUp(true);
                      setError(null);
                    }}
                    className="text-primary-400 hover:text-primary-300 font-medium"
                  >
                    Regístrate
                  </button>
                </>
              )}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

