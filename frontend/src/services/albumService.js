// This service handles all album-related operations

import { API_BASE_URL, apiCall } from '../config/api.js';
// Get all albums
export const getAlbums = async () => {
  try {
    const response = await apiCall(`${API_BASE_URL}/albums`);
    const albums = response.items || [];
    return albums.map(album => ({
      id: album.album_id,
      name: album.name,
      thumbnailUrl: album.thumbnail_urls?.[0]?.download_url || null,
      imageCount: album.image_count || 0
    }));
  } catch (error) {
    console.error('Failed to fetch albums:', error);
    throw new Error(`Failed to fetch albums: ${error.message}`);
  }
};

// Get a specific album by ID
export const getAlbum = async (albumId) => {
  try {
    // Get album metadata and images in a single call
    const response = await apiCall(`${API_BASE_URL}/albums/${albumId}`);
    const album = response.album;
    const images = response.images || [];
    
    return {
      id: album.album_id,
      name: album.name,
      description: album.description,
      imageCount: album.image_count || 0,
      images: images.map(image => ({
        id: image.image_id,
        name: image.name,
        url: image.download_url || '#',
        description: image.description
      }))
    };
  } catch (error) {
    console.error(`Failed to fetch album ${albumId}:`, error);
    throw new Error(`Failed to fetch album: ${error.message}`);
  }
};

// Create a new album
export const createAlbum = async (name, description = '') => {
  try {
    const newAlbum = await apiCall(`${API_BASE_URL}/albums`, {
      method: 'POST',
      body: JSON.stringify({ name, description })
    });
    
    return {
      id: newAlbum.album_id,
      name: newAlbum.name,
      description: newAlbum.description,
      thumbnailUrl: null,
      imageCount: 0
    };
  } catch (error) {
    console.error('Failed to create album:', error);
    throw new Error(`Failed to create album: ${error.message}`);
  }
};

// Download an album (in a real app, this would create a zip file)
export const downloadAlbum = async (albumId) => {
  try {
    // For now, this is a placeholder - the backend doesn't implement album download yet
    const album = await getAlbum(albumId);
    console.log(`Downloading album: ${album.name}`);
    alert(`Album download not yet implemented for: ${album.name}`);
  } catch (error) {
    console.error('Failed to download album:', error);
    throw new Error(`Failed to download album: ${error.message}`);
  }
};

// Download all albums (in a real app, this would create a zip file)
export const downloadAllAlbums = async () => {
  try {
    console.log('Downloading all albums');
    alert('Download all albums not yet implemented');
  } catch (error) {
    console.error('Failed to download all albums:', error);
    throw new Error(`Failed to download all albums: ${error.message}`);
  }
};