import React, { useState } from 'react';
import { XIcon } from 'lucide-react';
interface CreateAlbumModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateAlbum: (name: string) => void;
}
export function CreateAlbumModal({
  isOpen,
  onClose,
  onCreateAlbum
}: CreateAlbumModalProps) {
  const [albumName, setAlbumName] = useState('');
  if (!isOpen) return null;
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (albumName.trim()) {
      onCreateAlbum(albumName.trim());
      setAlbumName('');
      onClose();
    }
  };
  return <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md">
        <div className="flex justify-between items-center p-4 border-b">
          <h2 className="text-xl font-semibold">Create New Album</h2>
          <button onClick={onClose} className="p-1 rounded-full hover:bg-gray-100" aria-label="Close">
            <XIcon className="w-5 h-5 text-gray-600" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="p-4">
          <div className="mb-4">
            <label htmlFor="albumName" className="block text-sm font-medium text-gray-700 mb-1">
              Album Name
            </label>
            <input type="text" id="albumName" value={albumName} onChange={e => setAlbumName(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="Enter album name" required />
          </div>
          <div className="flex justify-end space-x-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200">
              Cancel
            </button>
            <button type="submit" className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700">
              Create
            </button>
          </div>
        </form>
      </div>
    </div>;
}