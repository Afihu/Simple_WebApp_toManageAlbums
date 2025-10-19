import React, { createElement } from 'react';
import { DownloadIcon } from 'lucide-react';
import { downloadImage } from '../services/imageService';

interface ImageCardProps {
  image: {
    id: string;
    url: string;
    name: string;
  };
  albumId: string;
  onImageClick: (image: ImageCardProps['image']) => void;
}
export function ImageCard({
  image,
  albumId,
  onImageClick
}: ImageCardProps) {
  const handleDownload = async (e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await downloadImage(albumId, image.id, image.name);
    } catch (error) {
      console.error('Failed to download image:', error);
      alert('Failed to download image. Please try again.');
    }
  };
  const handleImageClick = () => {
    onImageClick(image);
  };
  return <div className="group relative bg-white rounded-lg shadow-md overflow-hidden">
      <div className="h-48 bg-gray-100 cursor-pointer" onClick={handleImageClick}>
        <img src={image.url} alt={image.name} className="w-full h-full object-cover" />
      </div>
      <div className="p-3 flex justify-between items-center">
        <p className="text-sm text-gray-800 truncate">{image.name}</p>
        <button onClick={handleDownload} className="p-1 rounded-full hover:bg-gray-100" aria-label="Download image">
          <DownloadIcon className="w-4 h-4 text-gray-600" />
        </button>
      </div>
    </div>;
}