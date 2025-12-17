import { MessageSquare, Search, FolderOpen } from 'lucide-react';

/**
 * Tab navigation component
 * Allows switching between Ask, Search, and Documents views
 */
export default function TabNavigation({ activeTab, onTabChange }) {
  const tabs = [
    { id: 'ask', label: 'Preguntar', icon: MessageSquare },
    { id: 'search', label: 'Buscar', icon: Search },
    { id: 'upload', label: 'Documentos', icon: FolderOpen },
  ];

  return (
    <nav className="flex bg-dark-700 border-b border-dark-400">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;
        
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`
              flex-1 flex items-center justify-center gap-2 px-4 py-3
              text-sm font-medium transition-all duration-200
              ${isActive 
                ? 'text-primary-400 border-b-2 border-primary-500 bg-dark-600' 
                : 'text-dark-100 hover:text-dark-50 hover:bg-dark-600'
              }
            `}
          >
            <Icon className="w-4 h-4" />
            {tab.label}
          </button>
        );
      })}
    </nav>
  );
}
