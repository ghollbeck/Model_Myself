import React from 'react';

interface DocumentUploadProps {
    categoryOptions: string[];
    selectedCategory: string;
    showCategoryDropdown: boolean;
    setShowCategoryDropdown: (show: boolean) => void;
    handleCategorySelect: (option: string) => void;
    handleDrag: (e: React.DragEvent) => void;
    handleDrop: (e: React.DragEvent) => void;
    handleFileInput: (e: React.ChangeEvent<HTMLInputElement>) => void;
    uploadedFiles: File[];
    uploadFiles: () => void;
    formatFileSize: (bytes: number) => string;
    categoryDropdownRef: React.RefObject<HTMLDivElement>;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({
    categoryOptions,
    selectedCategory,
    showCategoryDropdown,
    setShowCategoryDropdown,
    handleCategorySelect,
    handleDrag,
    handleDrop,
    handleFileInput,
    uploadedFiles,
    uploadFiles,
    formatFileSize,
    categoryDropdownRef
}) => (
    <div className="card">
        <h3>📁 Document Upload</h3>
        <div className="upload-section">
            {/* Category Selection */}
            <div className="category-selection" style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#495057' }}>
                    📂 Select Category:
                </label>
                <div className="dropdown" ref={categoryDropdownRef} style={{ position: 'relative' }}>
                    <button 
                        className="dropdown-btn"
                        onClick={() => setShowCategoryDropdown(!showCategoryDropdown)}
                        style={{ 
                            width: '100%', 
                            padding: '10px 15px', 
                            backgroundColor: selectedCategory ? '#e8f5e8' : '#f8f9fa',
                            border: '1px solid #ddd',
                            borderRadius: '4px',
                            cursor: 'pointer'
                        }}
                    >
                        <span>{selectedCategory || 'Choose category...'}</span>
                        <span style={{ float: 'right' }}>▼</span>
                    </button>
                    {showCategoryDropdown && (
                        <div className="dropdown-content" style={{
                            position: 'absolute',
                            top: '100%',
                            left: '0',
                            right: '0',
                            zIndex: 1000,
                            backgroundColor: 'white',
                            border: '1px solid #ddd',
                            borderRadius: '4px',
                            boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
                            maxHeight: '200px',
                            overflowY: 'auto'
                        }}>
                            {categoryOptions.map((option, index) => (
                                <div 
                                    key={index}
                                    className="dropdown-item"
                                    onClick={() => handleCategorySelect(option)}
                                    style={{
                                        padding: '10px 15px',
                                        cursor: 'pointer',
                                        borderBottom: index < categoryOptions.length - 1 ? '1px solid #f0f0f0' : 'none'
                                    }}
                                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f5f5f5'}
                                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'white'}
                                >
                                    {option}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            <div 
                className={`upload-area`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
            >
                <p>Drag & drop files here or click to select</p>
                <input
                    type="file"
                    multiple
                    onChange={handleFileInput}
                    style={{ display: 'none' }}
                    id="fileInput"
                />
                <label htmlFor="fileInput" className="upload-btn">
                    Select Files
                </label>
            </div>
            
            {uploadedFiles.length > 0 && (
                <div className="file-list">
                    <h4 style={{color: '#495057', fontSize: '1.1em', marginBottom: '10px'}}>Selected Files:</h4>
                    {uploadedFiles.map((file, index) => (
                        <div key={index} className="file-item">
                            {file.name} ({formatFileSize(file.size)})
                        </div>
                    ))}
                    <button onClick={uploadFiles} className="upload-button">
                        Upload to MongoDB ({uploadedFiles.length} file(s))
                        {selectedCategory && <span style={{ display: 'block', fontSize: '0.8em', opacity: 0.8 }}>Category: {selectedCategory}</span>}
                    </button>
                </div>
            )}
        </div>
    </div>
);

export default DocumentUpload; 