from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Optional, Union
import json
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Training data file path
TRAINING_DATA_FILE = "training_data.json"

class TrainingAnswer(BaseModel):
    question_id: str
    question: str
    answer: Union[str, List[str]]  # Text answer or multiple choice selection
    answer_type: str  # "text" or "multiple_choice"
    category: str
    timestamp: datetime

class TrainingSession(BaseModel):
    category: str
    answers: List[TrainingAnswer]

# Predefined questions for each training category
TRAINING_QUESTIONS = {
    "Questions about my knowledge": [
        {
            "id": "knowledge_1",
            "question": "What are your main areas of expertise?",
            "type": "text",
            "placeholder": "e.g., programming, cooking, history..."
        },
        {
            "id": "knowledge_2", 
            "question": "Which subjects do you find most challenging?",
            "type": "text",
            "placeholder": "e.g., mathematics, public speaking..."
        },
        {
            "id": "knowledge_3",
            "question": "What's your preferred learning style?",
            "type": "multiple_choice",
            "options": ["Visual", "Auditory", "Kinesthetic", "Reading/Writing", "Mixed"]
        },
        {
            "id": "knowledge_4",
            "question": "How do you typically approach learning new topics?",
            "type": "multiple_choice",
            "options": ["Research extensively first", "Jump in and learn by doing", "Find a mentor/teacher", "Take structured courses", "Mix of approaches"]
        },
        {
            "id": "knowledge_5",
            "question": "What knowledge would you like to develop further?",
            "type": "text",
            "placeholder": "Areas you want to grow in..."
        }
    ],
    
    "Questions about my feelings and 5 personalities": [
        {
            "id": "personality_1",
            "question": "How do you typically handle stress?",
            "type": "multiple_choice",
            "options": ["Stay calm and analytical", "Seek support from others", "Take breaks and recharge", "Push through with determination", "Avoid stressful situations"]
        },
        {
            "id": "personality_2",
            "question": "In social situations, you tend to be:",
            "type": "multiple_choice",
            "options": ["Outgoing and talkative", "Quiet but engaged", "Reserved until comfortable", "The life of the party", "Prefer small groups"]
        },
        {
            "id": "personality_3",
            "question": "How do you make important decisions?",
            "type": "multiple_choice",
            "options": ["Logical analysis", "Follow intuition", "Seek others' opinions", "Consider all possibilities", "Go with past experience"]
        },
        {
            "id": "personality_4",
            "question": "What motivates you most?",
            "type": "text",
            "placeholder": "What drives you to achieve your goals..."
        },
        {
            "id": "personality_5",
            "question": "How do you handle change?",
            "type": "multiple_choice",
            "options": ["Embrace it eagerly", "Adapt gradually", "Need time to adjust", "Prefer stability", "Depends on the situation"]
        }
    ],
    
    "Question about the importance of people in my life": [
        {
            "id": "people_1",
            "question": "Who are the most important people in your life and why?",
            "type": "text",
            "placeholder": "Family, friends, mentors, colleagues..."
        },
        {
            "id": "people_2",
            "question": "How do you typically maintain relationships?",
            "type": "multiple_choice",
            "options": ["Regular contact", "Quality time together", "Helping when needed", "Sharing experiences", "Being a good listener"]
        },
        {
            "id": "people_3",
            "question": "What qualities do you value most in others?",
            "type": "text",
            "placeholder": "Honesty, loyalty, humor, intelligence..."
        },
        {
            "id": "people_4",
            "question": "How do you handle conflicts with important people?",
            "type": "multiple_choice",
            "options": ["Address directly", "Give it time", "Seek mediation", "Avoid confrontation", "Compromise"]
        },
        {
            "id": "people_5",
            "question": "What role do you play in your social circles?",
            "type": "multiple_choice",
            "options": ["The organizer", "The supporter", "The advisor", "The entertainer", "The peacemaker"]
        }
    ],
    
    "Iteratively add to a knowledge graph": [
        {
            "id": "graph_1",
            "question": "What key concepts define who you are?",
            "type": "text",
            "placeholder": "Core concepts, values, interests..."
        },
        {
            "id": "graph_2",
            "question": "How do your interests and skills connect to each other?",
            "type": "text",
            "placeholder": "Relationships between different aspects of yourself..."
        },
        {
            "id": "graph_3",
            "question": "What experiences have shaped your current knowledge?",
            "type": "text",
            "placeholder": "Key learning experiences, failures, successes..."
        },
        {
            "id": "graph_4",
            "question": "Which areas of knowledge would you like to explore connections for?",
            "type": "multiple_choice",
            "options": ["Personal values", "Professional skills", "Relationships", "Hobbies", "Life experiences"]
        },
        {
            "id": "graph_5",
            "question": "How do you see your knowledge evolving over time?",
            "type": "text",
            "placeholder": "Future learning goals, connections to build..."
        }
    ],
    
    "Preferences": [
        {
            "id": "pref_1",
            "question": "What's your ideal way to spend free time?",
            "type": "text",
            "placeholder": "Activities, hobbies, relaxation..."
        },
        {
            "id": "pref_2",
            "question": "In work/study environments, you prefer:",
            "type": "multiple_choice",
            "options": ["Quiet and focused", "Collaborative and social", "Flexible and changing", "Structured and organized", "Creative and inspiring"]
        },
        {
            "id": "pref_3",
            "question": "What type of challenges do you enjoy most?",
            "type": "multiple_choice",
            "options": ["Analytical problems", "Creative projects", "Social interactions", "Physical activities", "Learning new skills"]
        },
        {
            "id": "pref_4",
            "question": "How do you prefer to communicate?",
            "type": "multiple_choice",
            "options": ["Face-to-face", "Written messages", "Video calls", "Phone calls", "Depends on situation"]
        },
        {
            "id": "pref_5",
            "question": "What kind of feedback do you find most helpful?",
            "type": "text",
            "placeholder": "Direct, supportive, detailed, brief..."
        }
    ],
    
    "Moral questions": [
        {
            "id": "moral_1",
            "question": "What core values guide your decisions?",
            "type": "text",
            "placeholder": "Honesty, fairness, compassion, freedom..."
        },
        {
            "id": "moral_2",
            "question": "When facing an ethical dilemma, you typically:",
            "type": "multiple_choice",
            "options": ["Consider consequences", "Follow principles", "Seek guidance", "Trust intuition", "Weigh all perspectives"]
        },
        {
            "id": "moral_3",
            "question": "How important is it to you to help others?",
            "type": "multiple_choice",
            "options": ["Extremely important", "Very important", "Somewhat important", "Depends on situation", "Not a priority"]
        },
        {
            "id": "moral_4",
            "question": "What does 'doing the right thing' mean to you?",
            "type": "text",
            "placeholder": "Your personal definition of moral behavior..."
        },
        {
            "id": "moral_5",
            "question": "How do you handle situations where your values conflict?",
            "type": "text",
            "placeholder": "Your approach to moral conflicts..."
        }
    ],
    
    "Automatic questions to extend known knowledge": [
        {
            "id": "auto_1",
            "question": "What topics would you like to be asked about regularly?",
            "type": "text",
            "placeholder": "Areas for continuous learning..."
        },
        {
            "id": "auto_2",
            "question": "How often would you like to receive knowledge-building questions?",
            "type": "multiple_choice",
            "options": ["Daily", "Weekly", "Bi-weekly", "Monthly", "When I request them"]
        },
        {
            "id": "auto_3",
            "question": "What format works best for you to reflect on knowledge?",
            "type": "multiple_choice",
            "options": ["Short questions", "Deep reflections", "Comparisons", "Hypothetical scenarios", "Mixed formats"]
        },
        {
            "id": "auto_4",
            "question": "Which areas of your knowledge need the most development?",
            "type": "text",
            "placeholder": "Knowledge gaps you'd like to address..."
        },
        {
            "id": "auto_5",
            "question": "How do you prefer to track your learning progress?",
            "type": "multiple_choice",
            "options": ["Written journal", "Digital notes", "Progress charts", "Discussion with others", "Mental reflection"]
        }
    ]
}

def load_training_data():
    """Load existing training data from JSON file"""
    if os.path.exists(TRAINING_DATA_FILE):
        try:
            with open(TRAINING_DATA_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading training data: {e}")
            return []
    return []

def save_training_data(data):
    """Save training data to JSON file"""
    try:
        with open(TRAINING_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Training data saved successfully")
    except Exception as e:
        logger.error(f"Error saving training data: {e}")
        raise

@router.get("/questions/{category}")
async def get_training_questions(category: str):
    """Get predefined questions for a specific training category"""
    logger.info(f"Getting questions for category: {category}")
    
    if category not in TRAINING_QUESTIONS:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    
    questions = TRAINING_QUESTIONS[category]
    logger.info(f"Returning {len(questions)} questions for category: {category}")
    
    return {
        "category": category,
        "questions": questions,
        "total_questions": len(questions)
    }

@router.post("/answer")
async def save_training_answer(answer: TrainingAnswer):
    """Save a single training answer"""
    logger.info(f"Saving answer for question: {answer.question_id} in category: {answer.category}")
    
    # Load existing training data
    training_data = load_training_data()
    
    # Add new answer with timestamp
    answer_dict = answer.dict()
    answer_dict["timestamp"] = datetime.now().isoformat()
    
    training_data.append(answer_dict)
    
    # Save updated data
    save_training_data(training_data)
    
    logger.info(f"Answer saved successfully for question: {answer.question_id}")
    
    return {
        "message": "Answer saved successfully",
        "question_id": answer.question_id,
        "category": answer.category,
        "timestamp": answer_dict["timestamp"]
    }

@router.post("/session")
async def save_training_session(session: TrainingSession):
    """Save a complete training session with multiple answers"""
    logger.info(f"Saving training session for category: {session.category} with {len(session.answers)} answers")
    
    # Load existing training data
    training_data = load_training_data()
    
    # Add all answers from the session
    for answer in session.answers:
        answer_dict = answer.dict()
        answer_dict["timestamp"] = datetime.now().isoformat()
        training_data.append(answer_dict)
    
    # Save updated data
    save_training_data(training_data)
    
    logger.info(f"Training session saved successfully for category: {session.category}")
    
    return {
        "message": "Training session saved successfully",
        "category": session.category,
        "answers_saved": len(session.answers),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/data")
async def get_training_data(category: Optional[str] = None):
    """Get all training data or filter by category"""
    logger.info(f"Getting training data, category filter: {category}")
    
    training_data = load_training_data()
    
    if category:
        training_data = [item for item in training_data if item.get("category") == category]
    
    logger.info(f"Returning {len(training_data)} training records")
    
    return {
        "training_data": training_data,
        "total_records": len(training_data),
        "category_filter": category
    }

@router.get("/stats")
async def get_training_stats():
    """Get statistics about training data"""
    logger.info("Getting training statistics")
    
    training_data = load_training_data()
    
    # Count by category
    category_counts = {}
    for item in training_data:
        category = item.get("category", "Unknown")
        category_counts[category] = category_counts.get(category, 0) + 1
    
    # Count by answer type
    type_counts = {}
    for item in training_data:
        answer_type = item.get("answer_type", "Unknown")
        type_counts[answer_type] = type_counts.get(answer_type, 0) + 1
    
    stats = {
        "total_answers": len(training_data),
        "categories": category_counts,
        "answer_types": type_counts,
        "available_categories": list(TRAINING_QUESTIONS.keys())
    }
    
    logger.info(f"Training stats: {stats}")
    
    return stats 