import React, { useEffect, useState } from 'react';
import { Header } from './components/Header';
import { HomePage } from './pages/HomePage';
import { AlbumPage } from './pages/AlbumPage';
import { initRouter, getCurrentRoute } from './services/routeService';
export function App() {
  const [currentRoute, setCurrentRoute] = useState(getCurrentRoute());
  useEffect(() => {
    // Initialize the hash-based router
    initRouter(() => {
      setCurrentRoute(getCurrentRoute());
    });
  }, []);
  // Render the appropriate page based on the current route
  const renderContent = () => {
    // Route format: #/album/[albumId]
    if (currentRoute.startsWith('/album/')) {
      const albumId = currentRoute.split('/album/')[1];
      return <AlbumPage albumId={albumId} />;
    }
    // Default to home page
    return <HomePage />;
  };
  return <div className="flex flex-col w-full min-h-screen bg-gray-50">
      <Header />
      <main className="flex-1 container mx-auto px-4 py-6">
        {renderContent()}
      </main>
    </div>;
}