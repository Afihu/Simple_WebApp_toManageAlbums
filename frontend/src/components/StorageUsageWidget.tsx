import React from 'react';
interface StorageUsageWidgetProps {
  usedStorage: number; // in MB
  totalStorage: number; // in MB
}
export function StorageUsageWidget({
  usedStorage,
  totalStorage
}: StorageUsageWidgetProps) {
  const usagePercentage = Math.min(100, Math.round(usedStorage / totalStorage * 100));
  const formattedUsed = usedStorage >= 1000 ? `${(usedStorage / 1000).toFixed(1)} GB` : `${Math.round(usedStorage)} MB`;
  const formattedTotal = totalStorage >= 1000 ? `${(totalStorage / 1000).toFixed(1)} GB` : `${Math.round(totalStorage)} MB`;
  // Determine color based on usage percentage
  const getColorClass = () => {
    if (usagePercentage < 70) return 'bg-blue-500';
    if (usagePercentage < 90) return 'bg-yellow-500';
    return 'bg-red-500';
  };
  return <div className="bg-white rounded-full shadow-sm px-4 py-2 flex flex-col items-center max-w-xs mx-auto">
      <div className="text-sm font-medium text-gray-700 mb-1">
        {formattedUsed} / {formattedTotal} used
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5 mb-1">
        <div className={`h-2.5 rounded-full ${getColorClass()}`} style={{
        width: `${usagePercentage}%`
      }}></div>
      </div>
      <div className="text-xs text-gray-500">
        {usagePercentage}% of storage used
      </div>
    </div>;
}