import React from 'react';

interface ProfilePopupProps {
    showPopup: boolean;
    closePopup: () => void;
    popupTitle: string;
    popupContent: string;
    popupCategories: string[];
    openPopup: (category: string) => void;
    setPopupTitle: (title: string) => void;
    setPopupContent: (content: string) => void;
}

const ProfilePopup: React.FC<ProfilePopupProps> = ({
    showPopup,
    closePopup,
    popupTitle,
    popupContent,
    popupCategories,
    openPopup,
    setPopupTitle,
    setPopupContent
}) => (
    showPopup ? (
        <div className="popup-overlay" onClick={closePopup}>
            <div className="popup-content" onClick={(e) => e.stopPropagation()}>
                <div className="popup-header">
                    <h2>{popupTitle || 'Explore My Profile'}</h2>
                    <button className="close-btn" onClick={closePopup}>×</button>
                </div>
                {!popupTitle ? (
                    <div className="popup-body">
                        <p style={{textAlign: 'center', marginBottom: '30px', color: '#666'}}>
                            Choose a category to explore:
                        </p>
                        <div className="category-grid">
                            {popupCategories.map((category, index) => (
                                <button
                                    key={index}
                                    onClick={() => openPopup(category)}
                                    className="category-btn"
                                >
                                    {category}
                                </button>
                            ))}
                        </div>
                    </div>
                ) : (
                    <div className="popup-body">
                        <button 
                            onClick={() => {setPopupTitle(''); setPopupContent('')}}
                            className="back-btn"
                        >
                            ← Back to Categories
                        </button>
                        <div className="content-display">
                            <pre>{popupContent}</pre>
                        </div>
                    </div>
                )}
            </div>
        </div>
    ) : null
);

export default ProfilePopup; 