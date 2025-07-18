import React, { useState, useEffect } from 'react';
import { getTrainingQuestions, saveTrainingAnswer } from '../utils/api';

interface Question {
    id: string;
    question: string;
    type: 'text' | 'multiple_choice';
    placeholder?: string;
    options?: string[];
    answered?: boolean;
    existing_answer?: string | string[];
    answer_timestamp?: string;
}

interface TrainingPopupProps {
    showPopup: boolean;
    category: string;
    onClose: () => void;
    onLog: (message: string) => void;
    onTrainingComplete?: () => void;
}

const TrainingPopup: React.FC<TrainingPopupProps> = ({ showPopup, category, onClose, onLog, onTrainingComplete }) => {
    const [questions, setQuestions] = useState<Question[]>([]);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [answer, setAnswer] = useState<string>('');
    const [selectedOptions, setSelectedOptions] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string>('');
    const [answers, setAnswers] = useState<any[]>([]);
    const [hasAnswered, setHasAnswered] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [progressData, setProgressData] = useState<{answered_questions: number, progress_percentage: number} | null>(null);
    const [unsavedAnswers, setUnsavedAnswers] = useState<Set<number>>(new Set());
    const [unsavedAnswerData, setUnsavedAnswerData] = useState<{[key: number]: string | string[]}>({});

    useEffect(() => {
        if (showPopup && category) {
            fetchQuestions();
        }
    }, [showPopup, category]);

    useEffect(() => {
        // Load existing answer for current question
        if (questions.length > 0 && currentQuestionIndex < questions.length) {
            const currentQuestion = questions[currentQuestionIndex];
            if (currentQuestion.answered && currentQuestion.existing_answer) {
                if (currentQuestion.type === 'multiple_choice') {
                    setSelectedOptions(Array.isArray(currentQuestion.existing_answer) ? currentQuestion.existing_answer : [currentQuestion.existing_answer]);
                } else {
                    setAnswer(typeof currentQuestion.existing_answer === 'string' ? currentQuestion.existing_answer : currentQuestion.existing_answer[0] || '');
                }
                setHasAnswered(true);
            } else {
                setAnswer('');
                setSelectedOptions([]);
                setHasAnswered(false);
            }
        }
    }, [currentQuestionIndex, questions]);

    const fetchQuestions = async () => {
        try {
            setLoading(true);
            setError('');
            onLog(`Fetching questions for category: ${category}`);
            
            const data = await getTrainingQuestions(category);
            
            setQuestions(data.questions);
            setProgressData({
                answered_questions: data.answered_questions,
                progress_percentage: data.progress_percentage
            });
            setCurrentQuestionIndex(0);
            setAnswer('');
            setSelectedOptions([]);
            setAnswers([]);
            setHasAnswered(false);
            setUnsavedAnswers(new Set());
            setUnsavedAnswerData({});
            
            onLog(`Loaded ${data.questions.length} questions for ${category} (${data.answered_questions} already answered)`);
        } catch (err: any) {
            const errorMessage = err.message || 'Failed to fetch questions';
            setError(errorMessage);
            onLog(`Error fetching questions: ${errorMessage}`);
        } finally {
            setLoading(false);
        }
    };

    const saveProgress = async () => {
        if (unsavedAnswers.size === 0) {
            setError('No unsaved answers to save');
            return;
        }

        try {
            setIsSaving(true);
            setError('');
            
            const updatedQuestions = [...questions];
            const savedAnswers: any[] = [];
            
            // Save all unsaved answers
            for (const questionIndex of Array.from(unsavedAnswers)) {
                const question = questions[questionIndex];
                if (!question) continue;
                
                // Get the answer from our stored unsaved answer data
                const answerToSave = unsavedAnswerData[questionIndex];
                
                // Validate answer
                if (!answerToSave || (Array.isArray(answerToSave) && answerToSave.length === 0)) {
                    continue; // Skip if no valid answer
                }

                // Prepare answer data
                const answerData = {
                    question_id: question.id,
                    question: question.question,
                    answer: answerToSave,
                    answer_type: question.type,
                    category: category,
                    timestamp: new Date().toISOString()
                };

                // Save answer using the API function
                await saveTrainingAnswer(answerData);
                
                // Update the question as answered
                updatedQuestions[questionIndex] = {
                    ...updatedQuestions[questionIndex],
                    answered: true,
                    existing_answer: answerToSave,
                    answer_timestamp: answerData.timestamp
                };
                
                savedAnswers.push(answerData);
            }
            
            // Update questions state
            setQuestions(updatedQuestions);
            
            // Update progress
            const answeredCount = updatedQuestions.filter(q => q.answered).length;
            setProgressData({
                answered_questions: answeredCount,
                progress_percentage: (answeredCount / updatedQuestions.length) * 100
            });
            
            // Add to local answers array
            setAnswers(prev => [...prev, ...savedAnswers]);
            
            // Clear unsaved answers
            setUnsavedAnswers(new Set());
            setUnsavedAnswerData({});
            
            onLog(`Progress saved for ${savedAnswers.length} question(s)`);
            
            // Call completion callback to refresh knowledge graph
            if (onTrainingComplete) {
                onTrainingComplete();
            }
            
        } catch (err: any) {
            const errorMessage = err.message || 'Failed to save progress';
            setError(errorMessage);
            onLog(`Error saving progress: ${errorMessage}`);
        } finally {
            setIsSaving(false);
        }
    };

    const handleNextQuestion = () => {
        if (currentQuestionIndex < questions.length - 1) {
            setCurrentQuestionIndex(currentQuestionIndex + 1);
            setError('');
        } else {
            // All questions completed
            onLog(`Training session completed for ${category}!`);
            onLog('All answers have been saved automatically.');
            onClose();
        }
    };

    const handlePreviousQuestion = () => {
        if (currentQuestionIndex > 0) {
            setCurrentQuestionIndex(currentQuestionIndex - 1);
            setError('');
        }
    };

    const handleAnswerChange = (newAnswer: string | string[]) => {
        if (Array.isArray(newAnswer)) {
            setSelectedOptions(newAnswer);
        } else {
            setAnswer(newAnswer);
        }
        setHasAnswered(true);
        
        // Track this question as having an unsaved answer if it has content
        if (newAnswer && (Array.isArray(newAnswer) ? newAnswer.length > 0 : newAnswer.trim().length > 0)) {
            setUnsavedAnswers(prev => new Set([...Array.from(prev), currentQuestionIndex]));
            setUnsavedAnswerData(prev => ({ ...prev, [currentQuestionIndex]: newAnswer }));
        } else {
            // If answer is empty, remove from unsaved answers
            setUnsavedAnswers(prev => {
                const newSet = new Set(Array.from(prev));
                newSet.delete(currentQuestionIndex);
                return newSet;
            });
            setUnsavedAnswerData(prev => {
                const newData = { ...prev };
                delete newData[currentQuestionIndex];
                return newData;
            });
        }
    };

    const handleOptionSelect = (option: string) => {
        const currentQuestion = questions[currentQuestionIndex];
        if (currentQuestion.type === 'multiple_choice') {
            // For multiple choice, allow only one selection
            handleAnswerChange([option]);
        }
    };

    const handleClose = () => {
        setQuestions([]);
        setCurrentQuestionIndex(0);
        setAnswer('');
        setSelectedOptions([]);
        setError('');
        setAnswers([]);
        setHasAnswered(false);
        setProgressData(null);
        setUnsavedAnswers(new Set());
        setUnsavedAnswerData({});
        onClose();
    };

    if (!showPopup) return null;

    const currentQuestion = questions[currentQuestionIndex];
    const progress = questions.length > 0 ? ((currentQuestionIndex + 1) / questions.length) * 100 : 0;
    const currentAnswer = currentQuestion?.type === 'multiple_choice' ? selectedOptions : answer;
    const hasCurrentAnswer = currentAnswer && (Array.isArray(currentAnswer) ? currentAnswer.length > 0 : currentAnswer.length > 0);

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
                    <div className="progress-info">
                        <p className="progress-text">
                            Question {currentQuestionIndex + 1} of {questions.length}
                        </p>
                        {progressData && (
                            <p className="progress-stats">
                                {progressData.answered_questions} answered ({progressData.progress_percentage.toFixed(1)}% complete)
                            </p>
                        )}
                    </div>
                </div>

                <div className="training-category">
                    <h3>{category}</h3>
                </div>

                {loading && <div className="loading">Loading...</div>}
                {error && <div className="error">{error}</div>}

                {currentQuestion && !loading && (
                    <div className="question-container">
                        <div className="question-header">
                            <h4 className="question-text">{currentQuestion.question}</h4>
                            {currentQuestion.answered && (
                                <span className="answered-indicator">✓ Answered</span>
                            )}
                        </div>
                        
                        <div className="question-content">
                            {currentQuestion.type === 'text' && (
                                <div className="text-input-container">
                                    <textarea
                                        value={answer}
                                        onChange={(e) => handleAnswerChange(e.target.value)}
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
                        </div>

                        <div className="training-actions">
                            <div className="navigation-buttons">
                                <button 
                                    className="nav-btn prev-btn"
                                    onClick={handlePreviousQuestion}
                                    disabled={currentQuestionIndex === 0}
                                >
                                    ← Previous
                                </button>
                                
                                <button 
                                    className="nav-btn next-btn"
                                    onClick={handleNextQuestion}
                                    disabled={currentQuestionIndex === questions.length - 1}
                                >
                                    Next →
                                </button>
                            </div>
                            
                            <button 
                                className="save-progress-btn"
                                onClick={saveProgress}
                                disabled={isSaving || unsavedAnswers.size === 0}
                            >
                                {isSaving ? 'Saving...' : `Save Progress ${unsavedAnswers.size > 0 ? `(${unsavedAnswers.size})` : ''}`}
                            </button>
                            
                            <button 
                                className="finish-btn"
                                onClick={handleClose}
                            >
                                {currentQuestionIndex === questions.length - 1 ? 'Finish' : 'Close'}
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default TrainingPopup; 