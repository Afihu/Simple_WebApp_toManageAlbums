import React from 'react';
import { FolderIcon } from 'lucide-react';
interface AlbumCardProps {
  album: {
    id: string;
    name: string;
    thumbnailUrl?: string;
    imageCount: number;
  };
}
export function AlbumCard({
  album
}: AlbumCardProps) {
  const navigateToAlbum = () => {
    window.location.hash = `/album/${album.id}`;
  };
  return <div className="bg-white rounded-lg shadow-md overflow-hidden cursor-pointer hover:shadow-lg transition-shadow duration-200" onClick={navigateToAlbum}>
      <div className="h-40 bg-gray-100 flex items-center justify-center">
        {album.thumbnailUrl ? <img src={album.thumbnailUrl} alt={album.name} className="w-full h-full object-cover" /> : <FolderIcon className="w-16 h-16 text-gray-400" />}
      </div>
      <div className="p-4">
        <h3 className="font-medium text-gray-800">{album.name}</h3>
        <p className="text-sm text-gray-500 mt-1">{album.imageCount} photos</p>
      </div>
    </div>;
}