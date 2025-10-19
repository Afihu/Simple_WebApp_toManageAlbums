import React, { useEffect, useState } from 'react';
import { PlusIcon, DownloadIcon } from 'lucide-react';
import { AlbumCard } from '../components/AlbumCard';
import { CreateAlbumModal } from '../components/CreateAlbumModal';
import { getAlbums, createAlbum, downloadAllAlbums } from '../services/albumService';
export function HomePage() {
  const [albums, setAlbums] = useState<any[]>([]);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  useEffect(() => {
    loadAlbums();
  }, []);
  const loadAlbums = async () => {
    setIsLoading(true);
    try {
      const albumsData = await getAlbums();
      setAlbums(albumsData);
    } catch (error) {
      console.error('Failed to load albums:', error);
    } finally {
      setIsLoading(false);
    }
  };
  const handleCreateAlbum = async (name: string) => {
    try {
      const newAlbum = await createAlbum(name);
      setAlbums([...albums, newAlbum]);
    } catch (error) {
      console.error('Failed to create album:', error);
    }
  };
  const handleDownloadAll = async () => {
    try {
      await downloadAllAlbums();
    } catch (error) {
      console.error('Failed to download albums:', error);
    }
  };
  return <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">My Albums</h2>
        <div className="flex space-x-2">
          <button onClick={() => setIsCreateModalOpen(true)} className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
            <PlusIcon className="w-4 h-4 mr-1" />
            Create Album
          </button>
          {albums.length > 0 && <button onClick={handleDownloadAll} className="flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50">
              <DownloadIcon className="w-4 h-4 mr-1" />
              Download All
            </button>}
        </div>
      </div>
      {isLoading ? <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div> : albums.length === 0 ? <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <h3 className="text-lg font-medium text-gray-800 mb-2">
            No Albums Yet
          </h3>
          <p className="text-gray-600 mb-6">
            Create your first album to start organizing your photos
          </p>
          <button onClick={() => setIsCreateModalOpen(true)} className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
            Create Album
          </button>
        </div> : <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {albums.map(album => <AlbumCard key={album.id} album={album} />)}
        </div>}
      <CreateAlbumModal isOpen={isCreateModalOpen} onClose={() => setIsCreateModalOpen(false)} onCreateAlbum={handleCreateAlbum} />
    </div>;
}