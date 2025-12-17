import { useState } from 'react';
import Header from './components/Header';
import TabNavigation from './components/TabNavigation';
import ChatView from './components/ChatView';
import SearchView from './components/SearchView';
import UploadView from './components/UploadView';

/**
 * Main App Component
 * Manages tab navigation between the three main flows:
 * 1. Ask - Chat with AI about documents
 * 2. Search - Search document fragments
 * 3. Upload - Upload new documents
 */
export default function App() {
  const [activeTab, setActiveTab] = useState('ask');

  const renderContent = () => {
    switch (activeTab) {
      case 'ask':
        return <ChatView />;
      case 'search':
        return <SearchView />;
      case 'upload':
        return <UploadView />;
      default:
        return <ChatView />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl h-[90vh] bg-white rounded-2xl shadow-2xl overflow-hidden flex flex-col">
        <Header />
        <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />
        <main className="flex-1 overflow-hidden">
          {renderContent()}
        </main>
      </div>
    </div>
  );
}
