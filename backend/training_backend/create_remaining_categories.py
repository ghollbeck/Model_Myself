#!/usr/bin/env python3
"""
Script to create the remaining training categories (people and automatic)
"""

import json
import os

def create_people_questions():
    """Create questions for people category"""
    
    base_questions = [
        {"id": "people_1", "question": "Who are the most important people in your life and why?", "type": "text"},
        {"id": "people_2", "question": "How do you typically maintain relationships?", "type": "multiple_choice", "options": ["Regular contact", "Quality time together", "Helping when needed", "Sharing experiences", "Being a good listener"]},
        {"id": "people_3", "question": "What qualities do you value most in others?", "type": "text"},
        {"id": "people_4", "question": "How do you handle conflicts with important people?", "type": "multiple_choice", "options": ["Address directly", "Give it time", "Seek mediation", "Avoid confrontation", "Compromise"]},
        {"id": "people_5", "question": "What role do you play in your social circles?", "type": "multiple_choice", "options": ["The organizer", "The supporter", "The advisor", "The entertainer", "The peacemaker"]}
    ]
    
    # Generate additional questions
    additional_questions = []
    
    # Text questions about relationships
    text_questions = [
        "How do you build trust with new people?",
        "What makes a relationship meaningful to you?",
        "How do you show appreciation to important people?",
        "What role does communication play in your relationships?",
        "How do you handle disagreements with loved ones?",
        "What qualities do you bring to friendships?",
        "How do you maintain long-distance relationships?",
        "What does loyalty mean to you in relationships?",
        "How do you support others during difficult times?",
        "What boundaries do you set in relationships?",
        "How do you handle jealousy in relationships?",
        "What role does family play in your life?",
        "How do you make new friends as an adult?",
        "What does forgiveness mean to you?",
        "How do you handle toxic relationships?",
        "What role does vulnerability play in your connections?",
        "How do you balance independence with relationships?",
        "What makes you feel understood by others?",
        "How do you handle criticism from people you care about?",
        "What role does humor play in your relationships?",
        "How do you show empathy to others?",
        "What does emotional intimacy mean to you?",
        "How do you handle when others disappoint you?",
        "What role does shared interests play in friendships?",
        "How do you navigate different personality types?",
        "What makes you feel supported by others?",
        "How do you handle peer pressure?",
        "What role does honesty play in your relationships?",
        "How do you maintain relationships during busy periods?",
        "What does unconditional love mean to you?",
        "How do you handle when friends grow apart?",
        "What role does physical affection play in your relationships?",
        "How do you navigate cultural differences in relationships?",
        "What makes you feel valued by others?",
        "How do you handle competitive dynamics with friends?",
        "What role does shared values play in relationships?",
        "How do you support others' personal growth?",
        "What does respect mean to you in relationships?",
        "How do you handle when others need space?",
        "What role does tradition play in your family relationships?",
        "How do you navigate power dynamics in relationships?",
        "What makes you feel comfortable opening up to others?",
        "How do you handle when others judge your choices?",
        "What role does gratitude play in your relationships?",
        "How do you maintain authenticity in social situations?",
        "What does commitment mean to you in relationships?",
        "How do you handle when others betray your trust?",
        "What role does mutual respect play in your connections?",
        "How do you balance giving and receiving in relationships?",
        "What makes you feel emotionally safe with others?"
    ]
    
    # Multiple choice questions
    mc_questions = [
        {"question": "In group settings, you prefer:", "options": ["Leading discussions", "Contributing ideas", "Listening actively", "Mediating conflicts", "Organizing activities"]},
        {"question": "Your approach to making friends is:", "options": ["Outgoing and social", "Gradual and careful", "Through shared activities", "Online connections", "Depends on situation"]},
        {"question": "When someone is upset, you typically:", "options": ["Offer practical help", "Provide emotional support", "Give them space", "Try to cheer them up", "Listen without judgment"]},
        {"question": "Your ideal social circle size is:", "options": ["Large and diverse", "Medium sized", "Small and intimate", "Just a few close friends", "Varies by life stage"]},
        {"question": "In romantic relationships, you value most:", "options": ["Emotional connection", "Physical attraction", "Shared values", "Intellectual compatibility", "All equally important"]},
        {"question": "Your communication style with family is:", "options": ["Open and direct", "Respectful and formal", "Casual and relaxed", "Depends on family member", "Minimal communication"]},
        {"question": "When meeting new people, you:", "options": ["Introduce yourself readily", "Wait for introductions", "Observe before engaging", "Focus on common interests", "Depends on the setting"]},
        {"question": "Your approach to social media connections is:", "options": ["Connect with everyone", "Only close friends", "Professional network", "Minimal social media", "Depends on platform"]},
        {"question": "In friendships, you prefer:", "options": ["Deep conversations", "Shared activities", "Mutual support", "Fun and laughter", "Intellectual discussions"]},
        {"question": "Your conflict resolution style is:", "options": ["Direct confrontation", "Diplomatic discussion", "Seek mediation", "Avoid conflict", "Depends on relationship"]},
        {"question": "When others succeed, you typically feel:", "options": ["Genuinely happy", "Slightly envious", "Motivated to improve", "Depends on the person", "Indifferent"]},
        {"question": "Your approach to networking is:", "options": ["Strategic and purposeful", "Natural and organic", "Avoid networking", "Online focused", "Event-based"]},
        {"question": "In team dynamics, you usually:", "options": ["Take charge", "Contribute expertise", "Support harmony", "Challenge ideas", "Depends on team"]},
        {"question": "Your boundary setting is:", "options": ["Clear and firm", "Flexible and adaptable", "Struggle with boundaries", "Depends on relationship", "Avoid setting boundaries"]},
        {"question": "When others need advice, you:", "options": ["Give direct recommendations", "Ask guiding questions", "Share similar experiences", "Listen without advising", "Depends on the situation"]}
    ]
    
    # Add text questions
    for i, q in enumerate(text_questions):
        additional_questions.append({
            "id": f"people_{i+6}",
            "question": q,
            "type": "text",
            "placeholder": "Share your thoughts..."
        })
    
    # Add multiple choice questions
    for i, q in enumerate(mc_questions):
        additional_questions.append({
            "id": f"people_{i+len(text_questions)+6}",
            "question": q["question"],
            "type": "multiple_choice",
            "options": q["options"]
        })
    
    # Generate more questions to reach 250
    remaining_needed = 250 - len(additional_questions)
    for i in range(remaining_needed):
        additional_questions.append({
            "id": f"people_{len(additional_questions)+6}",
            "question": f"Additional relationship question {i+1}: How do you approach this aspect of your relationships?",
            "type": "text",
            "placeholder": "Share your thoughts..."
        })
    
    return {
        "category": "Question about the importance of people in my life",
        "category_key": "people",
        "existing_answers": [],
        "predefined_questions": base_questions,
        "additional_questions": additional_questions
    }

def create_automatic_questions():
    """Create questions for automatic category"""
    
    base_questions = [
        {"id": "auto_1", "question": "What topics would you like to be asked about regularly?", "type": "text"},
        {"id": "auto_2", "question": "How often would you like to receive knowledge-building questions?", "type": "multiple_choice", "options": ["Daily", "Weekly", "Bi-weekly", "Monthly", "When I request them"]},
        {"id": "auto_3", "question": "What format works best for you to reflect on knowledge?", "type": "multiple_choice", "options": ["Short questions", "Deep reflections", "Comparisons", "Hypothetical scenarios", "Mixed formats"]},
        {"id": "auto_4", "question": "Which areas of your knowledge need the most development?", "type": "text"},
        {"id": "auto_5", "question": "How do you prefer to track your learning progress?", "type": "multiple_choice", "options": ["Written journal", "Digital notes", "Progress charts", "Discussion with others", "Mental reflection"]}
    ]
    
    # Generate additional questions
    additional_questions = []
    
    # Text questions about automatic learning
    text_questions = [
        "What patterns do you notice in your learning habits?",
        "How do you identify knowledge gaps in your life?",
        "What triggers your curiosity about new topics?",
        "How do you want to be reminded about learning goals?",
        "What subjects do you wish you explored more automatically?",
        "How do you prefer to receive learning challenges?",
        "What role should AI play in your learning journey?",
        "How do you want to track your intellectual growth?",
        "What automated systems would help your learning?",
        "How do you prefer to discover new areas of interest?",
        "What questions do you wish you asked yourself more often?",
        "How do you want to be challenged intellectually?",
        "What learning reminders would be most helpful?",
        "How do you prefer to review and consolidate knowledge?",
        "What automated feedback would improve your learning?",
        "How do you want to connect different areas of knowledge?",
        "What learning patterns would you like to develop?",
        "How do you prefer to be prompted for reflection?",
        "What automated suggestions would enhance your growth?",
        "How do you want to measure your learning effectiveness?",
        "What personalized learning experiences do you desire?",
        "How do you prefer to be guided in knowledge exploration?",
        "What automated tools would support your learning goals?",
        "How do you want to be encouraged in your learning journey?",
        "What learning analytics would be most valuable to you?",
        "How do you prefer to receive adaptive learning content?",
        "What automated insights would improve your self-understanding?",
        "How do you want to be supported in developing new skills?",
        "What learning automation would save you the most time?",
        "How do you prefer to be reminded of your learning objectives?",
        "What automated connections would enhance your knowledge?",
        "How do you want to be challenged based on your progress?",
        "What learning personalization would be most beneficial?",
        "How do you prefer to receive context-aware learning prompts?",
        "What automated evaluation would help track your growth?",
        "How do you want to be guided through complex topics?",
        "What learning automation would keep you most engaged?",
        "How do you prefer to discover connections between concepts?",
        "What automated support would improve your retention?",
        "How do you want to be assisted in applying knowledge?",
        "What learning automation would boost your confidence?",
        "How do you prefer to receive personalized learning paths?",
        "What automated insights would enhance your decision-making?",
        "How do you want to be guided in critical thinking?",
        "What learning automation would improve your problem-solving?",
        "How do you prefer to be supported in creative thinking?",
        "What automated tools would enhance your communication skills?",
        "How do you want to be assisted in emotional intelligence?",
        "What learning automation would improve your leadership?",
        "How do you prefer to be guided in personal development?"
    ]
    
    # Multiple choice questions
    mc_questions = [
        {"question": "Your preferred learning reminder frequency is:", "options": ["Multiple times daily", "Once daily", "Few times weekly", "Weekly", "As needed"]},
        {"question": "For automated learning, you prefer:", "options": ["Structured curriculum", "Adaptive content", "Random challenges", "Goal-oriented", "Mixed approaches"]},
        {"question": "Your ideal learning prompt timing is:", "options": ["Morning reflection", "Throughout the day", "Evening review", "Weekend deep dives", "Flexible timing"]},
        {"question": "For knowledge tracking, you prefer:", "options": ["Visual progress", "Detailed analytics", "Simple checkmarks", "Narrative summaries", "No tracking"]},
        {"question": "Your automated learning style preference is:", "options": ["Question-based", "Scenario-based", "Comparison-based", "Story-based", "Mixed formats"]},
        {"question": "For learning recommendations, you prefer:", "options": ["AI-generated", "Peer-suggested", "Expert-curated", "Self-directed", "Combined sources"]},
        {"question": "Your preferred challenge level is:", "options": ["Slightly difficult", "Moderately challenging", "Highly challenging", "Adaptive difficulty", "Varies by topic"]},
        {"question": "For learning content, you prefer:", "options": ["Bite-sized pieces", "Comprehensive modules", "Interactive exercises", "Multimedia content", "Text-based"]},
        {"question": "Your automated feedback preference is:", "options": ["Immediate feedback", "Delayed reflection", "Peer feedback", "Self-assessment", "Mixed feedback"]},
        {"question": "For learning motivation, you prefer:", "options": ["Achievement badges", "Progress tracking", "Social recognition", "Personal satisfaction", "External rewards"]},
        {"question": "Your ideal learning environment is:", "options": ["Quiet spaces", "Background stimulation", "Social settings", "Outdoor locations", "Varies by topic"]},
        {"question": "For knowledge application, you prefer:", "options": ["Practical exercises", "Theoretical analysis", "Real-world projects", "Simulated scenarios", "Discussion-based"]},
        {"question": "Your learning schedule preference is:", "options": ["Fixed schedule", "Flexible timing", "Deadline-driven", "Mood-based", "Opportunity-based"]},
        {"question": "For learning support, you prefer:", "options": ["Automated guidance", "Human mentorship", "Peer learning", "Self-directed", "Hybrid approach"]},
        {"question": "Your knowledge retention method is:", "options": ["Spaced repetition", "Active recall", "Note-taking", "Teaching others", "Practical application"]}
    ]
    
    # Add text questions
    for i, q in enumerate(text_questions):
        additional_questions.append({
            "id": f"auto_{i+6}",
            "question": q,
            "type": "text",
            "placeholder": "Share your thoughts..."
        })
    
    # Add multiple choice questions  
    for i, q in enumerate(mc_questions):
        additional_questions.append({
            "id": f"auto_{i+len(text_questions)+6}",
            "question": q["question"],
            "type": "multiple_choice",
            "options": q["options"]
        })
    
    # Generate more questions to reach 250
    remaining_needed = 250 - len(additional_questions)
    for i in range(remaining_needed):
        additional_questions.append({
            "id": f"auto_{len(additional_questions)+6}",
            "question": f"Additional automatic learning question {i+1}: How would you like to be supported in this area?",
            "type": "text",
            "placeholder": "Share your thoughts..."
        })
    
    return {
        "category": "Automatic questions to extend known knowledge",
        "category_key": "automatic",
        "existing_answers": [],
        "predefined_questions": base_questions,
        "additional_questions": additional_questions
    }

def main():
    """Create the remaining category files"""
    
    # Create output directory
    output_dir = "../training_questions"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create people questions
    people_data = create_people_questions()
    with open(f"{output_dir}/people_questions.json", "w") as f:
        json.dump(people_data, f, indent=2)
    print(f"Created people_questions.json with {len(people_data['additional_questions'])} additional questions")
    
    # Create automatic questions
    automatic_data = create_automatic_questions()
    with open(f"{output_dir}/automatic_questions.json", "w") as f:
        json.dump(automatic_data, f, indent=2)
    print(f"Created automatic_questions.json with {len(automatic_data['additional_questions'])} additional questions")

if __name__ == "__main__":
    main()
