// This service handles quota and storage-related operations

import { API_BASE_URL, apiCall } from '../config/api.js';

// Get user's storage quota information
export const getStorageQuota = async () => {
  try {
    const quota = await apiCall(`${API_BASE_URL}/quota`);
    
    return {
      usedStorage: Math.round(quota.total_storage_bytes / (1024 * 1024)), // Convert to MB
      totalStorage: 5000, // 5GB default limit - TODO: make this configurable
      albumCount: quota.album_count || 0
    };
  } catch (error) {
    console.error('Failed to fetch storage quota:', error);
    // Return fallback values if API call fails
    return {
      usedStorage: 0,
      totalStorage: 5000,
      albumCount: 0
    };
  }
};