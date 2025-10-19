// This service handles all image-related operations with presigned URL workflow

import { API_BASE_URL, apiCall } from '../config/api.js';

// Upload images to an album using presigned URLs
export const uploadImages = async (albumId, files) => {
  const uploadPromises = files.map(async (file) => {
    try {
      console.log(`Starting upload for ${file.name}`);
      
      // Step 1: Get presigned upload URL
      const uploadUrlResponse = await apiCall(`${API_BASE_URL}/albums/${albumId}/images/upload-url`, {
        method: 'POST',
        body: JSON.stringify({
          name: file.name,
          description: '',
          content_type: file.type,
          size_bytes: file.size
        })
      });

      const { upload_url, image_id } = uploadUrlResponse;
      console.log(`Got presigned URL for ${file.name}, image_id: ${image_id}`);

      // Step 2: Upload file directly to S3 using presigned URL
      const uploadResponse = await fetch(upload_url, {
        method: 'PUT',
        body: file,
        headers: {
          'Content-Type': file.type,
        },
      });

      if (!uploadResponse.ok) {
        throw new Error(`Upload failed: ${uploadResponse.status}`);
      }

      console.log(`Successfully uploaded ${file.name} to S3`);

      // Step 3: Confirm upload completion
      const confirmResponse = await apiCall(`${API_BASE_URL}/albums/${albumId}/images/${image_id}/confirm`, {
        method: 'POST'
      });

      console.log(`Upload confirmed for ${file.name}`);

      return {
        id: image_id,
        name: file.name,
        url: confirmResponse.url || '#', // Use the confirmed image URL or placeholder
        status: 'uploaded'
      };

    } catch (error) {
      console.error(`Failed to upload ${file.name}:`, error);
      throw new Error(`Failed to upload ${file.name}: ${error.message}`);
    }
  });

  return Promise.all(uploadPromises);
};

// Download an image using presigned URL
export const downloadImage = async (albumId, imageId, imageName) => {
  try {
    console.log(`Starting download for ${imageName}`);
    
    // Get presigned download URL
    const downloadUrlResponse = await apiCall(`${API_BASE_URL}/albums/${albumId}/images/${imageId}/download-url`);
    
    const { download_url } = downloadUrlResponse;
    console.log(`Got presigned download URL for ${imageName}`);

    // Download the image using the presigned URL
    const imageResponse = await fetch(download_url);
    
    if (!imageResponse.ok) {
      throw new Error(`Download failed: ${imageResponse.status}`);
    }

    // Create blob and trigger download
    const blob = await imageResponse.blob();
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = imageName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Clean up the object URL
    URL.revokeObjectURL(url);
    
    console.log(`Successfully downloaded ${imageName}`);
  } catch (error) {
    console.error(`Failed to download ${imageName}:`, error);
    throw new Error(`Failed to download ${imageName}: ${error.message}`);
  }
};