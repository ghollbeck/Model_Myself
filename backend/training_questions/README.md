# Training Questions System

## Overview

This directory contains the organized training question system for the Model Myself application. The system has been refactored from hardcoded questions to a flexible JSON-based structure that supports extensive question libraries for each training category.

## File Structure

```
training_questions/
├── knowledge_questions.json      (355 questions)
├── personality_questions.json    (404 questions)
├── graph_questions.json          (250 questions)
├── moral_questions.json          (250 questions)
├── preferences_questions.json    (250 questions)
├── people_questions.json         (250 questions)
├── automatic_questions.json      (250 questions)
└── README.md                     (this file)
```

## Question Categories

### 1. Knowledge Questions (355 total)
- **File**: `knowledge_questions.json`
- **Purpose**: Assess learning styles, expertise areas, and knowledge development
- **Question Types**: Text input and multiple choice
- **Topics**: Learning methodologies, subject expertise, knowledge gaps, study approaches

### 2. Personality Questions (404 total)
- **File**: `personality_questions.json`
- **Purpose**: Explore personality traits, emotional responses, and behavioral patterns
- **Question Types**: Text input and multiple choice
- **Topics**: Stress handling, social behavior, decision-making, motivation, change adaptation

### 3. Graph Building Questions (250 total)
- **File**: `graph_questions.json`
- **Purpose**: Build knowledge graph connections and relationships
- **Question Types**: Text input and multiple choice
- **Topics**: Core concepts, interest connections, experience shaping, knowledge evolution

### 4. Moral Questions (250 total)
- **File**: `moral_questions.json`
- **Purpose**: Understand ethical values and moral decision-making
- **Question Types**: Text input and multiple choice
- **Topics**: Core values, ethical dilemmas, helping others, moral behavior, value conflicts

### 5. Preferences Questions (250 total)
- **File**: `preferences_questions.json`
- **Purpose**: Capture personal preferences and lifestyle choices
- **Question Types**: Text input and multiple choice
- **Topics**: Free time activities, work environments, communication styles, feedback preferences

### 6. People/Relationships Questions (250 total)
- **File**: `people_questions.json`
- **Purpose**: Explore relationship dynamics and social connections
- **Question Types**: Text input and multiple choice
- **Topics**: Important people, relationship maintenance, conflict resolution, social roles

### 7. Automatic Learning Questions (250 total)
- **File**: `automatic_questions.json`
- **Purpose**: Configure personalized learning systems and preferences
- **Question Types**: Text input and multiple choice
- **Topics**: Learning automation, knowledge tracking, personalized content, adaptive systems

## JSON Structure

Each question file follows this structure:

```json
{
  "category": "Human-readable category name",
  "category_key": "machine_readable_key",
  "existing_answers": [],
  "predefined_questions": [
    {
      "id": "category_1",
      "question": "Question text",
      "type": "text|multiple_choice",
      "options": ["Option 1", "Option 2", "..."] // Only for multiple_choice
    }
  ],
  "additional_questions": [
    // 250 additional questions following same structure
  ]
}
```

## API Integration

The training system integrates with the backend API through:

### Endpoints
- `GET /training/categories`: List all categories with question counts
- `GET /training/questions/{category}`: Get predefined questions for a category
- `GET /training/questions/{category}?all_questions=true`: Get all questions for a category
- `GET /training/stats`: Get statistics including available questions per category

### Functions
- `load_training_questions_from_file(category_key)`: Load questions from JSON file
- `get_category_questions(category)`: Get predefined questions for a category
- `get_all_category_questions(category)`: Get all questions for a category
- `get_available_categories()`: Get list of available categories

## Benefits

1. **Scalability**: Easy to add new questions and categories
2. **Maintainability**: Organized file structure for easy management
3. **Flexibility**: Support for both text and multiple choice questions
4. **API Integration**: Seamless integration with existing backend systems
5. **Extensibility**: Simple to add new question types or categories

## Usage

### Adding New Questions
1. Edit the appropriate JSON file
2. Add questions to the `additional_questions` array
3. Follow the existing ID pattern (e.g., `category_N`)
4. Ensure proper JSON formatting

### Adding New Categories
1. Create new JSON file following the naming pattern
2. Add category mapping to `CATEGORY_MAPPINGS` in `routes/training.py`
3. Update knowledge graph mappings if needed

## Total Questions Available

- **Total**: 2,059 questions across 7 categories
- **Predefined**: 35 questions (5 per category)
- **Additional**: 2,024 questions for extended training

## Backward Compatibility

The system maintains backward compatibility with existing training data while providing enhanced capabilities for comprehensive personality and knowledge assessment. 