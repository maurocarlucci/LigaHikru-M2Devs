/**
 * Loading spinner component
 * Displays a spinning indicator with optional text
 */
export default function Spinner({ text = 'Cargando...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-8">
      <div className="w-8 h-8 border-3 border-gray-200 border-t-primary-500 rounded-full animate-spin" />
      {text && <p className="mt-3 text-sm text-gray-500">{text}</p>}
    </div>
  );
}
