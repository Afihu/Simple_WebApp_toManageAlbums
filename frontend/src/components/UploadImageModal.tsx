import React, { useState, useRef } from 'react';
import { XIcon, UploadIcon } from 'lucide-react';
interface UploadImageModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadImages: (files: FileList) => void;
  albumId: string;
}
export function UploadImageModal({
  isOpen,
  onClose,
  onUploadImages,
  albumId
}: UploadImageModalProps) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  if (!isOpen) return null;
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setSelectedFiles(e.dataTransfer.files);
    }
  };
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFiles(e.target.files);
    }
  };
  const handleUpload = () => {
    if (selectedFiles) {
      onUploadImages(selectedFiles);
      onClose();
    }
  };
  return <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md">
        <div className="flex justify-between items-center p-4 border-b">
          <h2 className="text-xl font-semibold">Upload Images</h2>
          <button onClick={onClose} className="p-1 rounded-full hover:bg-gray-100" aria-label="Close">
            <XIcon className="w-5 h-5 text-gray-600" />
          </button>
        </div>
        <div className="p-4">
          <div className={`border-2 border-dashed rounded-lg p-8 text-center ${dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}`} onDragEnter={handleDrag} onDragOver={handleDrag} onDragLeave={handleDrag} onDrop={handleDrop}>
            <UploadIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-700 mb-2">
              Drag and drop your images here, or
            </p>
            <button type="button" onClick={() => fileInputRef.current?.click()} className="px-4 py-2 text-sm font-medium text-blue-600 bg-transparent border border-blue-600 rounded-md hover:bg-blue-50">
              Browse Files
            </button>
            <input ref={fileInputRef} type="file" multiple accept="image/*" onChange={handleFileChange} className="hidden" />
          </div>
          {selectedFiles && <div className="mt-4">
              <p className="text-sm font-medium text-gray-700 mb-2">
                Selected Files: {selectedFiles.length}
              </p>
              <div className="max-h-40 overflow-y-auto">
                {Array.from(selectedFiles).map((file, index) => <div key={index} className="text-sm text-gray-600 truncate">
                    {file.name}
                  </div>)}
              </div>
            </div>}
          <div className="flex justify-end space-x-2 mt-4">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200">
              Cancel
            </button>
            <button type="button" onClick={handleUpload} disabled={!selectedFiles} className={`px-4 py-2 text-sm font-medium text-white rounded-md ${selectedFiles ? 'bg-blue-600 hover:bg-blue-700' : 'bg-blue-400 cursor-not-allowed'}`}>
              Upload
            </button>
          </div>
        </div>
      </div>
    </div>;
}