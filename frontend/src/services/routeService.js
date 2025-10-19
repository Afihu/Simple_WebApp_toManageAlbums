// This service handles hash-based routing for the SPA
// Get the current route from the hash
export const getCurrentRoute = () => {
  // Remove the leading # and return the path
  const hash = window.location.hash;
  return hash.startsWith('#') ? hash.substring(1) : '/';
};
// Initialize the router
export const initRouter = onChange => {
  // Listen for hash changes
  window.addEventListener('hashchange', () => {
    onChange(getCurrentRoute());
  });
  // If no hash is present, set it to the root
  if (!window.location.hash) {
    window.location.hash = '/';
  }
};
// Navigate to a specific route
export const navigateTo = route => {
  window.location.hash = route;
};