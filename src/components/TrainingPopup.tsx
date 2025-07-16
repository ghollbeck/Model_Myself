import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Question {
    id: string;
    question: string;
    type: 'text' | 'multiple_choice';
    placeholder?: string;
    options?: string[];
}

interface TrainingPopupProps {
    showPopup: boolean;
    category: string;
    onClose: () => void;
    onLog: (message: string) => void;
}

const TrainingPopup: React.FC<TrainingPopupProps> = ({ showPopup, category, onClose, onLog }) => {
    const [questions, setQuestions] = useState<Question[]>([]);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [answer, setAnswer] = useState<string>('');
    const [selectedOptions, setSelectedOptions] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string>('');
    const [answers, setAnswers] = useState<any[]>([]);

    const API_BASE_URL = 'http://localhost:8089';

    useEffect(() => {
        if (showPopup && category) {
            fetchQuestions();
        }
    }, [showPopup, category]);

    const fetchQuestions = async () => {
        try {
            setLoading(true);
            setError('');
            onLog(`Fetching questions for category: ${category}`);
            
            const response = await axios.get(`${API_BASE_URL}/training/questions/${encodeURIComponent(category)}`);
            
            setQuestions(response.data.questions);
            setCurrentQuestionIndex(0);
            setAnswer('');
            setSelectedOptions([]);
            setAnswers([]);
            
            onLog(`Loaded ${response.data.questions.length} questions for ${category}`);
        } catch (err: any) {
            const errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch questions';
            setError(errorMessage);
            onLog(`Error fetching questions: ${errorMessage}`);
        } finally {
            setLoading(false);
        }
    };

    const handleNextQuestion = async () => {
        if (!questions[currentQuestionIndex]) return;
        
        const currentQuestion = questions[currentQuestionIndex];
        const currentAnswer = currentQuestion.type === 'multiple_choice' ? selectedOptions : answer;
        
        // Validate answer
        if (!currentAnswer || (Array.isArray(currentAnswer) && currentAnswer.length === 0)) {
            setError('Please provide an answer before proceeding');
            return;
        }

        try {
            setLoading(true);
            setError('');
            
            // Prepare answer data
            const answerData = {
                question_id: currentQuestion.id,
                question: currentQuestion.question,
                answer: currentAnswer,
                answer_type: currentQuestion.type,
                category: category,
                timestamp: new Date().toISOString()
            };

            // Save answer to backend
            await axios.post(`${API_BASE_URL}/training/answer`, answerData);
            
            // Add to local answers array
            setAnswers(prev => [...prev, answerData]);
            
            onLog(`Answer saved for question ${currentQuestionIndex + 1}/${questions.length}`);
            
            // Move to next question or finish
            if (currentQuestionIndex < questions.length - 1) {
                setCurrentQuestionIndex(currentQuestionIndex + 1);
                setAnswer('');
                setSelectedOptions([]);
            } else {
                // All questions completed
                onLog(`Training session completed for ${category}!`);
                onClose();
            }
            
        } catch (err: any) {
            const errorMessage = err.response?.data?.detail || err.message || 'Failed to save answer';
            setError(errorMessage);
            onLog(`Error saving answer: ${errorMessage}`);
        } finally {
            setLoading(false);
        }
    };

    const handleOptionSelect = (option: string) => {
        const currentQuestion = questions[currentQuestionIndex];
        if (currentQuestion.type === 'multiple_choice') {
            // For multiple choice, allow only one selection
            setSelectedOptions([option]);
        }
    };

    const handleClose = () => {
        setQuestions([]);
        setCurrentQuestionIndex(0);
        setAnswer('');
        setSelectedOptions([]);
        setError('');
        setAnswers([]);
        onClose();
    };

    if (!showPopup) return null;

    const currentQuestion = questions[currentQuestionIndex];
    const progress = questions.length > 0 ? ((currentQuestionIndex + 1) / questions.length) * 100 : 0;

    return (
        <div className="popup-overlay" onClick={handleClose}>
            <div className="popup-content training-popup" onClick={(e) => e.stopPropagation()}>
                <div className="popup-header">
                    <h2>🎯 Training Session</h2>
                    <button className="close-btn" onClick={handleClose}>×</button>
                </div>
                
                <div className="training-progress">
                    <div className="progress-bar">
                        <div className="progress-fill" style={{ width: `${progress}%` }}></div>
                    </div>
                    <p className="progress-text">
                        Question {currentQuestionIndex + 1} of {questions.length}
                    </p>
                </div>

                <div className="training-category">
                    <h3>{category}</h3>
                </div>

                {loading && <div className="loading">Loading...</div>}
                {error && <div className="error">{error}</div>}

                {currentQuestion && !loading && (
                    <div className="question-container">
                        <h4 className="question-text">{currentQuestion.question}</h4>
                        
                        {currentQuestion.type === 'text' && (
                            <div className="text-input-container">
                                <textarea
                                    value={answer}
                                    onChange={(e) => setAnswer(e.target.value)}
                                    placeholder={currentQuestion.placeholder || 'Enter your answer...'}
                                    className="training-textarea"
                                    rows={4}
                                />
                            </div>
                        )}

                        {currentQuestion.type === 'multiple_choice' && currentQuestion.options && (
                            <div className="multiple-choice-container">
                                {currentQuestion.options.map((option, index) => (
                                    <div 
                                        key={index}
                                        className={`choice-option ${selectedOptions.includes(option) ? 'selected' : ''}`}
                                        onClick={() => handleOptionSelect(option)}
                                    >
                                        <div className="choice-radio">
                                            {selectedOptions.includes(option) && <div className="radio-selected"></div>}
                                        </div>
                                        <span className="choice-text">{option}</span>
                                    </div>
                                ))}
                            </div>
                        )}

                        <div className="training-actions">
                            <button 
                                className="next-btn"
                                onClick={handleNextQuestion}
                                disabled={loading || (!answer && selectedOptions.length === 0)}
                            >
                                {currentQuestionIndex === questions.length - 1 ? 'Finish' : 'Next'}
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default TrainingPopup; 