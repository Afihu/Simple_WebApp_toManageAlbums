import React, { useState, useEffect } from 'react';
import { StorageUsageWidget } from './StorageUsageWidget';
import { getStorageQuota } from '../services/quotaService';

export function Header() {
  const [storageData, setStorageData] = useState({
    usedStorage: 0,
    totalStorage: 5000,
    albumCount: 0
  });
  
  const [isLoadingStorage, setIsLoadingStorage] = useState(true);

  useEffect(() => {
    const fetchStorageData = async () => {
      try {
        const quota = await getStorageQuota();
        setStorageData(quota);
      } catch (error) {
        console.error('Failed to fetch storage data:', error);
        // Keep default values if fetch fails
      } finally {
        setIsLoadingStorage(false);
      }
    };

    fetchStorageData();
  }, []);

  const handleLogout = () => {
    // This would typically call AWS Cognito logout
    console.log('Logout clicked');
    alert('Logging out...');
  };

  const navigateHome = () => {
    window.location.hash = '/';
  };

  return (
    <header className="bg-white shadow-sm">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800 cursor-pointer" onClick={navigateHome}>
          My Photo Albums
        </h1>
        <div className="flex-1 mx-4">
          {isLoadingStorage ? (
            <div className="text-sm text-gray-500">Loading storage info...</div>
          ) : (
            <StorageUsageWidget 
              usedStorage={storageData.usedStorage} 
              totalStorage={storageData.totalStorage} 
            />
          )}
        </div>
        <button 
          onClick={handleLogout} 
          className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200" 
          aria-label="Logout"
        >
          <div className="w-4 h-4 mr-1" />
          Logout
        </button>
      </div>
    </header>
  );
}