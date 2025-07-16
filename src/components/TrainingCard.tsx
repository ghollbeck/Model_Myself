import React, { useRef, useEffect } from 'react';

interface TrainingCardProps {
    trainingOptions: string[];
    selectedTraining: string;
    showTrainingDropdown: boolean;
    setShowTrainingDropdown: (show: boolean) => void;
    handleTrainingSelect: (option: string) => void;
    onStartTraining: () => void;
}

const TrainingCard: React.FC<TrainingCardProps> = ({
    trainingOptions,
    selectedTraining,
    showTrainingDropdown,
    setShowTrainingDropdown,
    handleTrainingSelect,
    onStartTraining
}) => {
    const dropdownRef = useRef<HTMLDivElement>(null);
    const buttonRef = useRef<HTMLButtonElement>(null);

    useEffect(() => {
        if (showTrainingDropdown && dropdownRef.current && buttonRef.current) {
            const button = buttonRef.current;
            const dropdown = dropdownRef.current;
            const buttonRect = button.getBoundingClientRect();
            const isMobile = window.innerWidth <= 768;

            if (isMobile) {
                // Position dropdown below the button with some margin
                dropdown.style.position = 'fixed';
                dropdown.style.top = `${buttonRect.bottom + 8}px`;
                dropdown.style.left = `${Math.max(10, buttonRect.left)}px`;
                dropdown.style.right = '10px';
                dropdown.style.width = 'auto';
                dropdown.style.maxWidth = `${Math.min(300, window.innerWidth - 20)}px`;
                dropdown.style.zIndex = '99999';
            }
        }
    }, [showTrainingDropdown]);

    return (
    <div className="card">
        <h3>🎯 Training</h3>
        <div className="training-section">
            <h4 style={{color: '#495057', fontSize: '1.1em', marginBottom: '15px'}}>Q&A Training Options:</h4>
            <div className="dropdown" style={{ position: 'relative' }}>
                <button 
                    ref={buttonRef}
                    className="dropdown-btn"
                    onClick={() => setShowTrainingDropdown(!showTrainingDropdown)}
                >
                    <span>{selectedTraining || 'Select Training Type'}</span>
                    <span>▼</span>
                </button>
                {showTrainingDropdown && (
                    <div ref={dropdownRef} className="dropdown-content">
                        {trainingOptions.map((option, index) => (
                            <div 
                                key={index}
                                className="dropdown-item"
                                onClick={() => handleTrainingSelect(option)}
                                style={{
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
                    <button 
                        className="start-training-btn"
                        onClick={onStartTraining}
                    >
                        Start Training
                    </button>
                </div>
            )}
        </div>
    </div>
    );
};

export default TrainingCard; 