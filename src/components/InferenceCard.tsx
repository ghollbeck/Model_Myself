import React from 'react';

interface InferenceCardProps {
    onInferenceClick: () => void;
}

const InferenceCard: React.FC<InferenceCardProps> = ({ onInferenceClick }) => {
    return (
        <div className="card">
            <h3>🧠 Inference</h3>
            <div className="inference-section">
                <h4 style={{color: '#495057', fontSize: '1.1em', marginBottom: '15px'}}>AI Inference Engine:</h4>
                <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    padding: '40px 20px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '10px',
                    border: '2px dashed #dee2e6',
                    minHeight: '200px'
                }}>
                    <div style={{
                        fontSize: '48px',
                        marginBottom: '20px',
                        opacity: '0.5'
                    }}>
                        🧠
                    </div>
                    <p style={{
                        textAlign: 'center',
                        color: '#6c757d',
                        margin: '0 0 20px 0',
                        fontSize: '1.1em',
                        fontWeight: '500'
                    }}>
                        AI Inference Ready
                    </p>
                    <button 
                        onClick={onInferenceClick}
                        style={{
                            backgroundColor: '#007bff',
                            color: 'white',
                            border: 'none',
                            padding: '12px 24px',
                            borderRadius: '8px',
                            fontSize: '1em',
                            fontWeight: '500',
                            cursor: 'pointer',
                            transition: 'all 0.3s ease',
                            boxShadow: '0 2px 4px rgba(0,123,255,0.3)'
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.backgroundColor = '#0056b3';
                            e.currentTarget.style.transform = 'translateY(-2px)';
                            e.currentTarget.style.boxShadow = '0 4px 8px rgba(0,123,255,0.4)';
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.backgroundColor = '#007bff';
                            e.currentTarget.style.transform = 'translateY(0)';
                            e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,123,255,0.3)';
                        }}
                    >
                        Start Inference
                    </button>
                </div>
            </div>
        </div>
    );
};

export default InferenceCard; 