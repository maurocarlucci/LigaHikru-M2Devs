import { MessageSquare, Search, Upload } from 'lucide-react';

/**
 * Tab navigation component
 * Allows switching between Ask, Search, and Upload views
 */
export default function TabNavigation({ activeTab, onTabChange }) {
  const tabs = [
    { id: 'ask', label: 'Preguntar', icon: MessageSquare },
    { id: 'search', label: 'Buscar', icon: Search },
    { id: 'upload', label: 'Subir', icon: Upload },
  ];

  return (
    <nav className="flex bg-gray-50 border-b-2 border-gray-200">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;
        
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`
              flex-1 flex items-center justify-center gap-2 px-4 py-3.5
              text-sm font-medium transition-all duration-200
              ${isActive 
                ? 'bg-white text-primary-600 border-b-3 border-primary-500' 
                : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
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
