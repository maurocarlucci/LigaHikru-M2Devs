import { useState, useEffect } from 'react';
import Header from './components/Header';
import TabNavigation from './components/TabNavigation';
import ChatView from './components/ChatView';
import SearchView from './components/SearchView';
import UploadView from './components/UploadView';
import LoginView from './components/LoginView';
import { isAuthenticated, getCurrentUser, logout } from './services/api';

/**
 * Main App Component
 * Manages tab navigation between the three main flows:
 * 1. Ask - Chat with AI about documents
 * 2. Search - Search document fragments
 * 3. Upload - Upload new documents
 */
export default function App() {
  const [activeTab, setActiveTab] = useState('ask');
  const [authenticated, setAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check authentication on mount
    checkAuth();
  }, []);

  const checkAuth = () => {
    const auth = isAuthenticated();
    if (auth) {
      const currentUser = getCurrentUser();
      setUser(currentUser);
    }
    setAuthenticated(auth);
    setLoading(false);
  };

  const handleLoginSuccess = () => {
    checkAuth();
  };

  const handleLogout = () => {
    logout();
    setAuthenticated(false);
    setUser(null);
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'ask':
        return <ChatView />;
      case 'search':
        return <SearchView />;
      case 'upload':
        // Only allow admins to access upload view
        if (user?.role === 'admin') {
          return <UploadView user={user} />;
        }
        // If somehow a non-admin gets here, redirect to ask
        return <ChatView />;
      default:
        return <ChatView />;
    }
  };

  // If user is not admin and tries to access upload, redirect to ask
  useEffect(() => {
    if (activeTab === 'upload' && user?.role !== 'admin') {
      setActiveTab('ask');
    }
  }, [activeTab, user]);

  // Show loading state
  if (loading) {
    return (
      <div className="h-screen bg-dark-800 flex items-center justify-center">
        <div className="text-dark-200">Cargando...</div>
      </div>
    );
  }

  // Show login if not authenticated
  if (!authenticated) {
    return <LoginView onLoginSuccess={handleLoginSuccess} />;
  }

  // Show main app if authenticated
  return (
    <div className="h-screen bg-dark-800 flex flex-col overflow-hidden">
      <Header user={user} onLogout={handleLogout} />
      <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} user={user} />
      <main className="flex-1 overflow-hidden">
        {renderContent()}
      </main>
    </div>
  );
}
