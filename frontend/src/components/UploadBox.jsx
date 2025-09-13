import { useState } from 'react';

export default function UploadBox({ onFilesUploaded }) {
  const [isDragging, setIsDragging] = useState(false);
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };
  
  const handleDragLeave = () => {
    setIsDragging(false);
  };
  
  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    handleFiles(droppedFiles);
  };
  
  const handleFileInput = (e) => {
    const selectedFiles = Array.from(e.target.files);
    handleFiles(selectedFiles);
  };
  
  const handleFiles = (newFiles) => {
    // Filter for valid file types
    const validFiles = newFiles.filter(file => {
      const fileType = file.type;
      return fileType.includes('pdf') || 
             fileType.includes('word') || 
             fileType.includes('text') ||
             fileType.includes('document');
    });
    
    setFiles(prev => [...prev, ...validFiles]);
  };
  
  const removeFile = (indexToRemove) => {
    setFiles(files.filter((_, index) => index !== indexToRemove));
  };
  
  const uploadFiles = () => {
    if (files.length === 0) return;
    
    setUploading(true);
    // Simulate API call
    setTimeout(() => {
      setUploading(false);
      setUploadSuccess(true);
      
      // Call the parent component's handler
      if (onFilesUploaded) {
        onFilesUploaded(files.length);
      }
      
      // Reset success state after showing animation
      setTimeout(() => {
        setFiles([]);
        setUploadSuccess(false);
      }, 2000);
    }, 2000);
  };

  return (
    <div className={`p-6 bg-white rounded-xl shadow-sm border w-full transition-all duration-300 ${uploadSuccess ? 'border-green-300 bg-green-50' : ''}`}>
      <h2 className="text-lg font-semibold mb-2">Document Upload</h2>
      <p className="text-sm text-gray-500 mb-4">
        Upload your regulatory documents for GxP compliance validation.
        Supported formats: PDF, Word, Text files.
      </p>

      <div 
        className={`border-2 border-dashed rounded-lg p-10 flex flex-col items-center justify-center text-gray-500 cursor-pointer transition-all
          ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:bg-gray-50'}
          ${uploadSuccess ? 'border-green-500 bg-green-50' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => document.getElementById('fileInput').click()}
      >
        {uploadSuccess ? (
          <div className="flex flex-col items-center text-green-600 animate-bounce">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <p className="font-medium">Upload Successful!</p>
          </div>
        ) : (
          <>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className={`h-10 w-10 mb-2 ${isDragging ? 'text-blue-500' : 'text-gray-400'}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1M12 12V4m0 8l-3-3m3 3l3-3" />
            </svg>
            <p className="text-sm font-medium">{isDragging ? 'Drop files here' : 'Drop files here or click to browse'}</p>
            <p className="text-xs text-gray-400 mt-1">
              PDF, Word documents, and text files up to 10MB each
            </p>
          </>
        )}
        <input 
          type="file" 
          id="fileInput" 
          multiple 
          className="hidden" 
          onChange={handleFileInput}
          accept=".pdf,.doc,.docx,.txt" 
        />
      </div>
      
      {files.length > 0 && (
        <div className="mt-4">
          <h3 className="text-sm font-medium mb-2">Selected Files ({files.length})</h3>
          <div className="space-y-2 max-h-40 overflow-y-auto custom-scrollbar">
            {files.map((file, index) => (
              <div key={index} className="flex items-center justify-between bg-gray-50 p-2 rounded-lg">
                <div className="flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-gray-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span className="text-sm truncate max-w-xs">{file.name}</span>
                </div>
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile(index);
                  }} 
                  className="text-red-500 hover:text-red-700"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
          <button 
            className={`mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center`}
            disabled={uploading || files.length === 0}
            onClick={uploadFiles}
          >
            {uploading ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Uploading...
              </>
            ) : 'Upload Files'}
          </button>
        </div>
      )}
    </div>
  );
}