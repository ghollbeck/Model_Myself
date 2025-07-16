import React from 'react';

interface TrainingCardProps {
    trainingOptions: string[];
    selectedTraining: string;
    showTrainingDropdown: boolean;
    setShowTrainingDropdown: (show: boolean) => void;
    handleTrainingSelect: (option: string) => void;
}

const TrainingCard: React.FC<TrainingCardProps> = ({
    trainingOptions,
    selectedTraining,
    showTrainingDropdown,
    setShowTrainingDropdown,
    handleTrainingSelect
}) => (
    <div className="card">
        <h3>🎯 Training</h3>
        <div className="training-section">
            <h4 style={{color: '#495057', fontSize: '1.1em', marginBottom: '15px'}}>Q&A Training Options:</h4>
            <div className="dropdown" style={{ position: 'relative' }}>
                <button 
                    className="dropdown-btn"
                    onClick={() => setShowTrainingDropdown(!showTrainingDropdown)}
                >
                    <span>{selectedTraining || 'Select Training Type'}</span>
                    <span>▼</span>
                </button>
                {showTrainingDropdown && (
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
                        {trainingOptions.map((option, index) => (
                            <div 
                                key={index}
                                className="dropdown-item"
                                onClick={() => handleTrainingSelect(option)}
                                style={{
                                    padding: '10px 15px',
                                    cursor: 'pointer',
                                    borderBottom: index < trainingOptions.length - 1 ? '1px solid #f0f0f0' : 'none'
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
            {selectedTraining && (
                <div className="selected-training">
                    <p>Selected: <strong>{selectedTraining}</strong></p>
                    <button className="start-training-btn">
                        Start Training
                    </button>
                </div>
            )}
        </div>
    </div>
);

export default TrainingCard; 