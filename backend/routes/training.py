from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Optional, Union
import json
import os
from datetime import datetime
import logging
import sys
from pathlib import Path

# Add the parent directory to the path to import the knowledge graph
sys.path.append(str(Path(__file__).parent.parent))
try:
    from analysis.graph import KnowledgeGraph
except ImportError:
    KnowledgeGraph = None
    print("Warning: Could not import KnowledgeGraph. Training data will not be synced to knowledge graph.")

logger = logging.getLogger(__name__)

router = APIRouter()

# Training data file path
TRAINING_DATA_FILE = "training_data.json"
TRAINING_QUESTIONS_DIR = "training_questions"

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

# Category mappings
CATEGORY_MAPPINGS = {
    "Questions about my knowledge": "knowledge",
    "Questions about my feelings and 5 personalities": "personality",
    "Question about the importance of people in my life": "people",
    "Iteratively add to a knowledge graph": "graph",
    "Preferences": "preferences",
    "Moral questions": "moral",
    "Automatic questions to extend known knowledge": "automatic"
}

def load_training_questions_from_file(category_key: str) -> Dict:
    """Load training questions from JSON file"""
    filename = f"{TRAINING_QUESTIONS_DIR}/{category_key}_questions.json"
    
    if not os.path.exists(filename):
        logger.error(f"Training questions file not found: {filename}")
        return {}
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        return data
    except Exception as e:
        logger.error(f"Error loading training questions from {filename}: {e}")
        return {}

def get_category_questions(category: str) -> List[Dict]:
    """Get questions for a specific category"""
    category_key = CATEGORY_MAPPINGS.get(category)
    if not category_key:
        logger.error(f"Unknown category: {category}")
        return []
    
    category_data = load_training_questions_from_file(category_key)
    if not category_data:
        return []
    
    # Return first 5 predefined questions for now
    return category_data.get("predefined_questions", [])

def get_all_category_questions(category: str) -> List[Dict]:
    """Get all questions (predefined + additional) for a specific category"""
    category_key = CATEGORY_MAPPINGS.get(category)
    if not category_key:
        logger.error(f"Unknown category: {category}")
        return []
    
    category_data = load_training_questions_from_file(category_key)
    if not category_data:
        return []
    
    # Combine predefined and additional questions
    all_questions = category_data.get("predefined_questions", []) + category_data.get("additional_questions", [])
    return all_questions

def get_available_categories() -> List[str]:
    """Get list of available training categories"""
    return list(CATEGORY_MAPPINGS.keys())

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

def save_training_data(data: List[Dict]):
    """Save training data to JSON file"""
    try:
        with open(TRAINING_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved {len(data)} training records")
    except Exception as e:
        logger.error(f"Error saving training data: {e}")
        raise

def sync_knowledge_graph():
    """Sync training data with knowledge graph"""
    if KnowledgeGraph is None:
        logger.warning("KnowledgeGraph not available, skipping sync")
        return
    
    try:
        kg = KnowledgeGraph()
        
        # Try to load existing graph
        try:
            kg.load("knowledge_graph.pkl")
        except Exception as e:
            logger.info(f"No existing graph found, creating new one: {e}")
            # Create example data
            kg.add_entry("Knowledge", "What is your expertise?", "AI, coding, philosophy")
            kg.add_entry("Feelings", "How do you feel today?", "Curious and motivated")
            kg.add_entry("Personalities", "Which of the Big Five fits you best?", "Openness to experience")
            kg.add_entry("ImportanceOfPeople", "Who is most important in your life?", "Family and close friends")
            kg.add_entry("Preferences", "What is your favorite hobby?", "Reading science fiction")
            kg.add_entry("Morals", "Is honesty always the best policy?", "Usually, but context matters")
            kg.add_entry("AutomaticQuestions", "What would you like to learn next?", "Graph databases")
        
        # Sync with training data
        kg.sync_with_training_data(TRAINING_DATA_FILE)
        
        # Save the updated graph
        kg.save("knowledge_graph.pkl")
        
        logger.info("Successfully synchronized training data with knowledge graph")
        
    except Exception as e:
        logger.error(f"Error syncing knowledge graph: {e}")

def get_existing_answers_for_category(category: str) -> Dict[str, Dict]:
    """Get existing answers for a specific category"""
    training_data = load_training_data()
    existing_answers = {}
    
    for item in training_data:
        if item.get("category") == category:
            question_id = item.get("question_id")
            if question_id:
                existing_answers[question_id] = {
                    "answer": item.get("answer"),
                    "answer_type": item.get("answer_type"),
                    "timestamp": item.get("timestamp")
                }
    
    return existing_answers

def enhance_questions_with_answers(questions: List[Dict], existing_answers: Dict[str, Dict]) -> List[Dict]:
    """Add existing answer information to questions"""
    enhanced_questions = []
    
    for question in questions:
        question_id = question.get("id")
        enhanced_question = question.copy()
        
        if question_id in existing_answers:
            enhanced_question["existing_answer"] = existing_answers[question_id]["answer"]
            enhanced_question["answered"] = True
            enhanced_question["answer_timestamp"] = existing_answers[question_id]["timestamp"]
        else:
            enhanced_question["answered"] = False
            enhanced_question["existing_answer"] = None
            enhanced_question["answer_timestamp"] = None
        
        enhanced_questions.append(enhanced_question)
    
    return enhanced_questions

@router.get("/questions/{category}")
async def get_training_questions(category: str, all_questions: bool = True):
    """Get questions for a specific training category with existing answers"""
    logger.info(f"Getting questions for category: {category}")
    
    if category not in CATEGORY_MAPPINGS:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    
    if all_questions:
        questions = get_all_category_questions(category)
    else:
        questions = get_category_questions(category)
    
    # Get existing answers for this category
    existing_answers = get_existing_answers_for_category(category)
    
    # Enhance questions with existing answer information
    enhanced_questions = enhance_questions_with_answers(questions, existing_answers)
    
    # Count answered questions
    answered_count = sum(1 for q in enhanced_questions if q["answered"])
    
    logger.info(f"Returning {len(enhanced_questions)} questions for category: {category} ({answered_count} answered)")
    
    return {
        "category": category,
        "questions": enhanced_questions,
        "total_questions": len(enhanced_questions),
        "answered_questions": answered_count,
        "progress_percentage": (answered_count / len(enhanced_questions)) * 100 if enhanced_questions else 0
    }

@router.get("/categories")
async def get_training_categories():
    """Get all available training categories"""
    logger.info("Getting all training categories")
    
    categories = get_available_categories()
    
    # Get question counts for each category
    category_info = []
    for category in categories:
        category_key = CATEGORY_MAPPINGS[category]
        category_data = load_training_questions_from_file(category_key)
        
        predefined_count = len(category_data.get("predefined_questions", []))
        additional_count = len(category_data.get("additional_questions", []))
        total_count = predefined_count + additional_count
        
        category_info.append({
            "category": category,
            "category_key": category_key,
            "predefined_questions": predefined_count,
            "additional_questions": additional_count,
            "total_questions": total_count
        })
    
    return {
        "categories": category_info,
        "total_categories": len(categories)
    }

@router.post("/answer")
async def save_training_answer(answer: TrainingAnswer):
    """Save a training answer"""
    logger.info(f"Saving answer for question {answer.question_id}")
    
    # Load existing data
    training_data = load_training_data()
    
    # Convert answer to dictionary
    answer_dict = {
        "question_id": answer.question_id,
        "question": answer.question,
        "answer": answer.answer,
        "answer_type": answer.answer_type,
        "category": answer.category,
        "timestamp": answer.timestamp.isoformat()
    }
    
    # Add to training data
    training_data.append(answer_dict)
    
    # Save back to file
    save_training_data(training_data)
    
    # Sync with knowledge graph
    sync_knowledge_graph()
    
    logger.info(f"Successfully saved answer for question {answer.question_id}")
    
    return {"message": "Answer saved successfully", "answer_id": answer.question_id}

@router.post("/session")
async def save_training_session(session: TrainingSession):
    """Save a complete training session"""
    logger.info(f"Saving training session for category: {session.category}")
    
    # Load existing data
    training_data = load_training_data()
    
    # Convert session answers to dictionaries
    for answer in session.answers:
        answer_dict = {
            "question_id": answer.question_id,
            "question": answer.question,
            "answer": answer.answer,
            "answer_type": answer.answer_type,
            "category": answer.category,
            "timestamp": answer.timestamp.isoformat()
        }
        training_data.append(answer_dict)
    
    # Save back to file
    save_training_data(training_data)
    
    # Sync with knowledge graph
    sync_knowledge_graph()
    
    logger.info(f"Successfully saved training session with {len(session.answers)} answers")
    
    return {
        "message": "Training session saved successfully",
        "category": session.category,
        "answers_saved": len(session.answers)
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
    
    # Get available questions count
    available_questions = {}
    for category in get_available_categories():
        category_key = CATEGORY_MAPPINGS[category]
        category_data = load_training_questions_from_file(category_key)
        total_available = len(category_data.get("predefined_questions", [])) + len(category_data.get("additional_questions", []))
        available_questions[category] = total_available
    
    stats = {
        "total_answers": len(training_data),
        "categories": category_counts,
        "answer_types": type_counts,
        "available_categories": get_available_categories(),
        "available_questions_per_category": available_questions
    }
    
    logger.info(f"Training stats: {stats}")
    
    return stats 