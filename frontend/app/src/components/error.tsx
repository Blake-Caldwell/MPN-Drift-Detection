import { useEffect } from 'react';

interface ErrorPopupProps {
  message: string;
  onClose: () => void;
}

const ErrorPopup: React.FC<ErrorPopupProps> = ({ message, onClose }) => {
  useEffect(() => {
    const outsideClickCall = (e: MouseEvent) => {
      const popupContent = document.querySelector('.popup-content');
      if (popupContent && !popupContent.contains(e.target as Node)) {
        onClose();
      }
    };

    document.addEventListener('mousedown', outsideClickCall);

    return () => {
      document.removeEventListener('mousedown', outsideClickCall);
    };
  }, [onClose]);

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50">
      <div className="bg-white p-6 flex flex-col items-center justify-center rounded-lg shadow-lg popup-content">
        <h3 className="text-xl text-black font-semibold mb-4">Error:</h3>
        <p className="text-lg font-semibold text-red-600 mb-6">{message}</p>
        <button
          onClick={onClose}
          className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
        >
          Close
        </button>
      </div>
    </div>
  );
};

export default ErrorPopup;
// continue here