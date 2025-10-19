import React, { useEffect } from 'react';
import { XIcon } from 'lucide-react';
interface ImageViewModalProps {
  isOpen: boolean;
  onClose: () => void;
  image: {
    id: string;
    url: string;
    name: string;
  } | null;
}
export function ImageViewModal({
  isOpen,
  onClose,
  image
}: ImageViewModalProps) {
  if (!isOpen || !image) return null;
  // Close when clicking the backdrop, but not when clicking the image
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };
  // Close on ESC key press
  useEffect(() => {
    const handleEscKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleEscKey);
    return () => {
      window.removeEventListener('keydown', handleEscKey);
    };
  }, [onClose]);
  return <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50" onClick={handleBackdropClick}>
      <div className="relative max-w-5xl max-h-[90vh] flex flex-col">
        <button onClick={onClose} className="absolute top-2 right-2 bg-black bg-opacity-50 text-white p-1 rounded-full hover:bg-opacity-70 z-10" aria-label="Close">
          <XIcon className="w-6 h-6" />
        </button>
        <div className="overflow-hidden rounded-lg">
          <img src={image.url} alt={image.name} className="max-h-[85vh] max-w-full object-contain" />
        </div>
        <div className="mt-2 bg-black bg-opacity-50 text-white p-2 rounded-lg text-center">
          <p className="text-sm truncate">{image.name}</p>
        </div>
      </div>
    </div>;
}