import { useState, useEffect } from 'react';

/**
 * Loading spinner component
 * Displays a spinning circle with animated "Pensando..." dots
 */
export default function Spinner({ text = 'Pensando' }) {
  const [dots, setDots] = useState('');

  useEffect(() => {
    const interval = setInterval(() => {
      setDots((prev) => (prev.length >= 3 ? '' : prev + '.'));
    }, 400);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center py-4">
      <div className="w-6 h-6 border-2 border-dark-300 border-t-primary-500 rounded-full animate-spin mb-2" />
      <p className="text-sm text-dark-100 min-w-[80px] text-center">
        {text}<span className="inline-block w-4 text-left">{dots}</span>
      </p>
    </div>
  );
}
