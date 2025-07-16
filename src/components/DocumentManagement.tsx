import React from 'react';

interface DocumentManagementProps {
    documents: any[];
    showDocuments: boolean;
    loadDocuments: () => void;
    deleteDocument: (documentId: string, filename: string) => void;
    downloadDocument: (documentId: string, filename: string) => void;
    formatFileSize: (bytes: number) => string;
    formatDate: (dateString: string) => string;
}

const DocumentManagement: React.FC<DocumentManagementProps> = ({
    documents,
    showDocuments,
    loadDocuments,
    deleteDocument,
    downloadDocument,
    formatFileSize,
    formatDate
}) => (
    <div className="card">
        <h3>📊 Document Management</h3>
        <div className="document-section">
            <div className="document-actions">
                <button onClick={loadDocuments} className="doc-btn">
                    📄 View Documents
                </button>
            </div>
            {showDocuments && documents.length > 0 && (
                <div className="documents-list">
                    <h4>📄 Stored Documents ({documents.length})</h4>
                    <div className="document-grid">
                        {documents.map((doc, index) => (
                            <div key={index} className="document-item">
                                <div className="doc-info">
                                    <strong>{doc.filename}</strong>
                                    <small>{formatFileSize(doc.file_size)} • {formatDate(doc.upload_date)}</small>
                                    {doc.category && (
                                        <div style={{ 
                                            backgroundColor: '#e8f5e8', 
                                            color: '#2d5a2d', 
                                            padding: '2px 6px', 
                                            borderRadius: '3px', 
                                            fontSize: '0.75em', 
                                            marginTop: '4px',
                                            display: 'inline-block'
                                        }}>
                                            📂 {doc.category}
                                        </div>
                                    )}
                                </div>
                                <div className="doc-actions">
                                    <button 
                                        onClick={() => deleteDocument(doc.id, doc.filename)}
                                        className="doc-action-btn delete"
                                    >
                                        🗑️
                                    </button>
                                    <button 
                                        onClick={() => downloadDocument(doc.id, doc.filename)}
                                        className="doc-action-btn download"
                                    >
                                        ⬇️
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    </div>
);

export default DocumentManagement; 