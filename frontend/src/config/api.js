// API Configuration
// This file centralizes API configuration for the frontend

// Base URL for the API Gateway
// In production, this could be loaded from environment variables or build-time configuration
export const API_BASE_URL = 'https://cmojmdhu9a.execute-api.ap-southeast-1.amazonaws.com/Dev';

// Authentication configuration
export const getAuthHeaders = () => {
  // TODO: Replace with actual JWT token from AWS Cognito
  // For development, we use the x-user-id header that the backend accepts
  return {
    'x-user-id': 'user-test-123', // Development fallback
    'Content-Type': 'application/json',
  };
};

// Helper function to make authenticated API calls
export const apiCall = async (url, options = {}) => {
  const response = await fetch(url, {
    headers: {
      ...getAuthHeaders(),
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Network error' }));
    throw new Error(error.message || error.error || `HTTP ${response.status}`);
  }

  return response.json();
};