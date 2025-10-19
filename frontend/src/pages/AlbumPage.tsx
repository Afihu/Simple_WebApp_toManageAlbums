import React, { useEffect, useState } from 'react';
import { ArrowLeftIcon, PlusIcon, DownloadIcon } from 'lucide-react';
import { ImageCard } from '../components/ImageCard';
import { UploadImageModal } from '../components/UploadImageModal';
import { ImageViewModal } from '../components/ImageViewModal';
import { getAlbum, downloadAlbum } from '../services/albumService';
import { uploadImages } from '../services/imageService';
interface AlbumPageProps {
  albumId: string;
}
export function AlbumPage({
  albumId
}: AlbumPageProps) {
  const [album, setAlbum] = useState<any>(null);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [viewedImage, setViewedImage] = useState<any>(null);
  const [isImageViewOpen, setIsImageViewOpen] = useState(false);
  useEffect(() => {
    loadAlbum();
  }, [albumId]);
  const loadAlbum = async () => {
    setIsLoading(true);
    try {
      const albumData = await getAlbum(albumId);
      setAlbum(albumData);
    } catch (error) {
      console.error('Failed to load album:', error);
    } finally {
      setIsLoading(false);
    }
  };
  const handleUploadImages = async (files: FileList) => {
    try {
      const newImages = await uploadImages(albumId, files);
      setAlbum({
        ...album,
        images: [...album.images, ...newImages]
      });
    } catch (error) {
      console.error('Failed to upload images:', error);
    }
  };
  const handleDownloadAlbum = async () => {
    try {
      await downloadAlbum(albumId);
    } catch (error) {
      console.error('Failed to download album:', error);
    }
  };
  const navigateBack = () => {
    window.location.hash = '/';
  };
  const handleImageClick = (image: any) => {
    setViewedImage(image);
    setIsImageViewOpen(true);
  };
  if (isLoading) {
    return <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>;
  }
  if (!album) {
    return <div className="text-center py-12">
        <h2 className="text-xl font-medium text-gray-800 mb-2">
          Album not found
        </h2>
        <button onClick={navigateBack} className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
          Back to Albums
        </button>
      </div>;
  }
  return <div>
      <div className="flex items-center mb-6">
        <button onClick={navigateBack} className="mr-4 p-2 rounded-full hover:bg-gray-100" aria-label="Go back">
          <ArrowLeftIcon className="w-5 h-5 text-gray-600" />
        </button>
        <h2 className="text-2xl font-bold text-gray-800">{album.name}</h2>
      </div>
      <div className="flex justify-between items-center mb-6">
        <p className="text-gray-600">{album.images.length} photos</p>
        <div className="flex space-x-2">
          <button onClick={() => setIsUploadModalOpen(true)} className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
            <PlusIcon className="w-4 h-4 mr-1" />
            Upload Images
          </button>
          {album.images.length > 0 && <button onClick={handleDownloadAlbum} className="flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50">
              <DownloadIcon className="w-4 h-4 mr-1" />
              Download Album
            </button>}
        </div>
      </div>
      {album.images.length === 0 ? <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <h3 className="text-lg font-medium text-gray-800 mb-2">
            No Images Yet
          </h3>
          <p className="text-gray-600 mb-6">
            Upload your first images to this album
          </p>
          <button onClick={() => setIsUploadModalOpen(true)} className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
            Upload Images
          </button>
        </div> : <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {album.images.map((image: any) => <ImageCard key={image.id} image={image} albumId={albumId} onImageClick={handleImageClick} />)}
        </div>}
      <UploadImageModal isOpen={isUploadModalOpen} onClose={() => setIsUploadModalOpen(false)} onUploadImages={handleUploadImages} albumId={albumId} />
      <ImageViewModal isOpen={isImageViewOpen} onClose={() => setIsImageViewOpen(false)} image={viewedImage} />
    </div>;
}