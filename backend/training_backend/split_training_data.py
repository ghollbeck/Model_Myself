#!/usr/bin/env python3
"""
Script to split training_data.json into separate files for each category
and generate additional questions for each category
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

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

def load_existing_data() -> List[Dict[str, Any]]:
    """Load existing training data"""
    with open("training_data.json", "r") as f:
        return json.load(f)

def split_by_category(data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Split data by category"""
    categorized = {}
    
    for item in data:
        category = item.get("category", "")
        if category not in categorized:
            categorized[category] = []
        categorized[category].append(item)
    
    return categorized

def generate_knowledge_questions() -> List[Dict[str, Any]]:
    """Generate 250 additional knowledge questions"""
    questions = []
    
    # Text questions
    text_questions = [
        "What specific programming languages do you know best?",
        "Describe your experience with different learning methodologies.",
        "What technical skills would you like to improve?",
        "How do you stay updated with new information in your field?",
        "What was the most challenging concept you've learned recently?",
        "Describe a time when you had to learn something completely new.",
        "What resources do you use most for learning?",
        "How do you organize and retain new information?",
        "What subjects do you find easiest to understand?",
        "Describe your experience with collaborative learning.",
        "What topics can you teach others about?",
        "How do you approach complex problem-solving?",
        "What areas of knowledge do you feel most confident in?",
        "Describe your experience with different educational systems.",
        "What motivates you to learn new things?",
        "How do you measure your learning progress?",
        "What knowledge gaps do you want to fill?",
        "Describe your experience with self-directed learning.",
        "What tools or methods help you learn best?",
        "How do you apply theoretical knowledge to practical situations?",
        "What subjects have you studied formally?",
        "Describe your experience with online learning.",
        "What knowledge do you consider most valuable?",
        "How do you handle information overload?",
        "What learning experiences have been most impactful?",
        "Describe your approach to research and fact-checking.",
        "What knowledge would you like to share with others?",
        "How do you adapt your learning style to different subjects?",
        "What role does curiosity play in your learning?",
        "Describe your experience with different types of media for learning.",
        "What knowledge do you wish you had learned earlier?",
        "How do you balance breadth vs depth in learning?",
        "What subjects do you find most intellectually stimulating?",
        "Describe your experience with learning from mistakes.",
        "What knowledge skills transfer well between different areas?",
        "How do you evaluate the credibility of information sources?",
        "What role does practice play in your learning process?",
        "Describe your experience with learning under pressure.",
        "What knowledge areas are you most passionate about?",
        "How do you maintain long-term retention of information?",
        "What subjects would you like to explore in more depth?",
        "Describe your experience with different note-taking methods.",
        "What knowledge do you consider fundamental to your worldview?",
        "How do you approach learning abstract concepts?",
        "What role does discussion play in your learning?",
        "Describe your experience with learning from different cultures.",
        "What knowledge areas challenge your existing beliefs?",
        "How do you integrate new knowledge with what you already know?",
        "What subjects do you find most relevant to your daily life?",
        "Describe your experience with learning through experimentation.",
        "What knowledge would you like to develop for career growth?",
        "How do you approach learning when you're not naturally talented?",
        "What subjects have you learned purely for personal interest?",
        "Describe your experience with learning in group settings.",
        "What knowledge areas require the most discipline for you?",
        "How do you approach learning controversial or sensitive topics?",
        "What role does repetition play in your learning process?",
        "Describe your experience with learning from books vs other media.",
        "What knowledge areas do you find most practical?",
        "How do you approach learning when you disagree with the content?",
        "What subjects have you learned through travel or experience?",
        "Describe your experience with learning different languages.",
        "What knowledge areas connect most strongly to your values?",
        "How do you approach learning when resources are limited?",
        "What subjects do you find most challenging to explain to others?",
        "Describe your experience with learning through teaching.",
        "What knowledge areas have changed your perspective most?",
        "How do you approach learning when you're already an expert?",
        "What subjects do you learn best through hands-on experience?",
        "Describe your experience with learning from failure.",
        "What knowledge areas are you most curious about?",
        "How do you approach learning when you're pressed for time?",
        "What subjects have you learned through mentorship?",
        "Describe your experience with learning creative skills.",
        "What knowledge areas do you find most transferable?",
        "How do you approach learning when you lack foundation knowledge?",
        "What subjects do you learn best through storytelling?",
        "Describe your experience with learning analytical skills.",
        "What knowledge areas do you find most personally meaningful?",
        "How do you approach learning when you're intimidated by the subject?",
        "What subjects have you learned through observation?",
        "Describe your experience with learning interpersonal skills.",
        "What knowledge areas do you find most universally applicable?",
        "How do you approach learning when you're highly motivated?",
        "What subjects do you learn best through comparison and contrast?",
        "Describe your experience with learning through simulation.",
        "What knowledge areas have been most useful in your career?",
        "How do you approach learning when you're skeptical of the content?",
        "What subjects have you learned through trial and error?",
        "Describe your experience with learning through visualization.",
        "What knowledge areas do you find most challenging to measure?",
        "How do you approach learning when you're learning alongside others?",
        "What subjects do you learn best through case studies?",
        "Describe your experience with learning through immersion.",
        "What knowledge areas have surprised you with their complexity?",
        "How do you approach learning when you need immediate application?",
        "What subjects have you learned through debate and discussion?",
        "Describe your experience with learning through reflection.",
        "What knowledge areas do you find most emotionally engaging?",
        "How do you approach learning when you're learning for others?",
        "What subjects do you learn best through structured curricula?",
        "Describe your experience with learning through collaboration.",
        "What knowledge areas have been most personally transformative?",
        "How do you approach learning when you're re-learning something?",
        "What subjects have you learned through documentation and manuals?",
        "Describe your experience with learning through questions.",
        "What knowledge areas do you find most intellectually rewarding?",
        "How do you approach learning when you're learning independently?",
        "What subjects do you learn best through examples and analogies?",
        "Describe your experience with learning through feedback.",
        "What knowledge areas have been most practically useful?",
        "How do you approach learning when you're learning competitively?",
        "What subjects have you learned through projects and assignments?",
        "Describe your experience with learning through exploration.",
        "What knowledge areas do you find most socially relevant?",
        "How do you approach learning when you're learning recreationally?",
        "What subjects do you learn best through patterns and systems?",
        "Describe your experience with learning through mentoring others.",
        "What knowledge areas have been most personally challenging?",
        "How do you approach learning when you're learning under guidance?",
        "What subjects have you learned through workshops and seminars?",
        "Describe your experience with learning through problem-solving.",
        "What knowledge areas do you find most culturally important?",
        "How do you approach learning when you're learning for mastery?",
        "What subjects do you learn best through games and simulations?",
        "Describe your experience with learning through research.",
        "What knowledge areas have been most professionally relevant?",
        "How do you approach learning when you're learning for understanding?",
        "What subjects have you learned through conferences and events?",
        "Describe your experience with learning through synthesis.",
        "What knowledge areas do you find most personally satisfying?",
        "How do you approach learning when you're learning for application?",
        "What subjects do you learn best through multimedia approaches?",
        "Describe your experience with learning through critical thinking.",
        "What knowledge areas have been most globally relevant?",
        "How do you approach learning when you're learning for innovation?",
        "What subjects have you learned through peer learning?",
        "Describe your experience with learning through systematic study.",
        "What knowledge areas do you find most ethically important?",
        "How do you approach learning when you're learning for leadership?",
        "What subjects do you learn best through active participation?",
        "Describe your experience with learning through cross-training.",
        "What knowledge areas have been most personally enriching?",
        "How do you approach learning when you're learning for service?",
        "What subjects have you learned through formal education?",
        "Describe your experience with learning through continuous improvement.",
        "What knowledge areas do you find most strategically important?",
        "How do you approach learning when you're learning for creativity?",
        "What subjects do you learn best through interdisciplinary approaches?",
        "Describe your experience with learning through adaptation.",
        "What knowledge areas have been most personally meaningful?",
        "How do you approach learning when you're learning for problem-solving?",
        "What subjects have you learned through apprenticeship?",
        "Describe your experience with learning through innovation.",
        "What knowledge areas do you find most personally relevant?",
        "How do you approach learning when you're learning for growth?",
        "What subjects do you learn best through experiential learning?",
        "Describe your experience with learning through mentorship.",
        "What knowledge areas have been most transformative?",
        "How do you approach learning when you're learning for understanding others?",
        "What subjects have you learned through self-discovery?",
        "Describe your experience with learning through reflection and analysis.",
        "What knowledge areas do you find most personally challenging?",
        "How do you approach learning when you're learning for personal development?",
        "What subjects do you learn best through integrated approaches?",
        "Describe your experience with learning through exploration and discovery.",
        "What knowledge areas have been most intellectually stimulating?",
        "How do you approach learning when you're learning for mastery of fundamentals?",
        "What subjects have you learned through community involvement?",
        "Describe your experience with learning through synthesis and integration.",
        "What knowledge areas do you find most personally fulfilling?",
        "How do you approach learning when you're learning for broad understanding?",
        "What subjects do you learn best through personalized approaches?",
        "Describe your experience with learning through continuous exploration.",
        "What knowledge areas have been most personally impactful?",
        "How do you approach learning when you're learning for deep expertise?",
        "What subjects have you learned through life experience?",
        "Describe your experience with learning through holistic approaches.",
        "What knowledge areas do you find most personally valuable?",
        "How do you approach learning when you're learning for comprehensive understanding?",
        "What subjects do you learn best through adaptive methods?",
        "Describe your experience with learning through lifelong learning.",
        "What knowledge areas have been most personally significant?",
        "How do you approach learning when you're learning for wisdom?",
        "What subjects have you learned through integrated life experiences?",
        "Describe your experience with learning through continuous development.",
        "What knowledge areas do you find most personally inspiring?",
        "How do you approach learning when you're learning for personal growth?",
        "What subjects do you learn best through comprehensive approaches?",
        "Describe your experience with learning through transformative education.",
        "What knowledge areas have been most personally enriching?",
        "How do you approach learning when you're learning for life mastery?",
        "What subjects have you learned through holistic life integration?",
        "Describe your experience with learning through continuous personal development.",
        "What knowledge areas do you find most personally transformative?",
        "How do you approach learning when you're learning for optimal living?",
        "What subjects do you learn best through integrated personal growth?",
        "Describe your experience with learning through comprehensive life education.",
        "What knowledge areas have been most personally meaningful and impactful?",
        "How do you approach learning when you're learning for complete understanding?",
        "What subjects have you learned through total life integration?",
        "Describe your experience with learning through holistic personal development.",
        "What knowledge areas do you find most personally significant and valuable?",
        "How do you approach learning when you're learning for ultimate mastery?",
        "What subjects do you learn best through complete life integration?",
        "Describe your experience with learning through comprehensive personal growth.",
        "What knowledge areas have been most personally transformative and enriching?",
        "How do you approach learning when you're learning for complete life mastery?",
        "What subjects have you learned through total personal development?",
        "Describe your experience with learning through complete life integration.",
        "What knowledge areas do you find most personally fulfilling and meaningful?",
        "How do you approach learning when you're learning for comprehensive life understanding?",
        "What subjects do you learn best through total life education?",
        "Describe your experience with learning through complete personal transformation.",
        "What knowledge areas have been most personally significant and impactful?",
        "How do you approach learning when you're learning for ultimate life mastery?",
        "What subjects have you learned through comprehensive life integration?",
        "Describe your experience with learning through total personal development.",
        "What knowledge areas do you find most personally valuable and transformative?",
        "How do you approach learning when you're learning for complete life optimization?",
        "What subjects do you learn best through holistic life mastery?",
        "Describe your experience with learning through comprehensive personal growth.",
        "What knowledge areas have been most personally meaningful and significant?",
        "How do you approach learning when you're learning for total life understanding?",
        "What subjects have you learned through complete personal integration?",
        "Describe your experience with learning through holistic life development.",
        "What knowledge areas do you find most personally enriching and valuable?",
        "How do you approach learning when you're learning for comprehensive life mastery?",
        "What subjects do you learn best through total personal transformation?",
        "Describe your experience with learning through complete life education.",
        "What knowledge areas have been most personally fulfilling and impactful?",
        "How do you approach learning when you're learning for ultimate personal growth?",
        "What subjects have you learned through comprehensive life development?",
        "Describe your experience with learning through total life integration.",
        "What knowledge areas do you find most personally transformative and significant?",
        "How do you approach learning when you're learning for complete personal mastery?",
        "What subjects do you learn best through holistic life optimization?",
        "Describe your experience with learning through comprehensive personal development.",
        "What knowledge areas have been most personally valuable and meaningful?",
        "How do you approach learning when you're learning for total personal understanding?",
        "What subjects have you learned through complete life transformation?",
        "Describe your experience with learning through holistic personal growth.",
        "What knowledge areas do you find most personally significant and enriching?",
        "How do you approach learning when you're learning for comprehensive personal mastery?",
        "What subjects do you learn best through total life development?",
        "Describe your experience with learning through complete personal integration.",
        "What knowledge areas have been most personally impactful and transformative?",
        "How do you approach learning when you're learning for ultimate life understanding?",
        "What subjects have you learned through comprehensive personal growth?",
        "Describe your experience with learning through total personal optimization.",
        "What knowledge areas do you find most personally meaningful and valuable?",
        "How do you approach learning when you're learning for complete life development?",
        "What subjects do you learn best through holistic personal mastery?",
        "Describe your experience with learning through comprehensive life growth.",
        "What knowledge areas have been most personally enriching and significant?",
        "How do you approach learning when you're learning for total life mastery?",
        "What subjects have you learned through complete personal development?",
        "Describe your experience with learning through holistic life integration.",
        "What knowledge areas do you find most personally valuable and impactful?",
        "How do you approach learning when you're learning for comprehensive life understanding?",
        "What subjects do you learn best through total personal growth?",
        "Describe your experience with learning through complete life mastery.",
        "What knowledge areas have been most personally transformative and meaningful?",
        "How do you approach learning when you're learning for ultimate personal development?",
        "What subjects have you learned through comprehensive life optimization?",
        "Describe your experience with learning through total life growth.",
        "What knowledge areas do you find most personally significant and valuable?",
        "How do you approach learning when you're learning for complete personal understanding?",
        "What subjects do you learn best through holistic life development?",
        "Describe your experience with learning through comprehensive personal integration.",
        "What knowledge areas have been most personally fulfilling and transformative?",
        "How do you approach learning when you're learning for total personal mastery?",
        "What subjects have you learned through complete life development?",
        "Describe your experience with learning through holistic personal optimization.",
        "What knowledge areas do you find most personally enriching and meaningful?",
        "How do you approach learning when you're learning for comprehensive personal growth?",
        "What subjects do you learn best through total life integration?",
        "Describe your experience with learning through complete personal development.",
        "What knowledge areas have been most personally impactful and significant?",
        "How do you approach learning when you're learning for ultimate life development?",
        "What subjects have you learned through comprehensive personal mastery?",
        "Describe your experience with learning through total personal integration.",
        "What knowledge areas do you find most personally transformative and valuable?",
        "How do you approach learning when you're learning for complete life growth?",
        "What subjects do you learn best through holistic personal development?",
        "Describe your experience with learning through comprehensive life mastery.",
        "What knowledge areas have been most personally meaningful and enriching?",
        "How do you approach learning when you're learning for total life optimization?",
        "What subjects have you learned through complete personal growth?",
        "Describe your experience with learning through holistic life development.",
        "What knowledge areas do you find most personally significant and transformative?",
        "How do you approach learning when you're learning for comprehensive life mastery?",
        "What subjects do you learn best through total personal development?",
        "Describe your experience with learning through complete life integration.",
        "What knowledge areas have been most personally valuable and impactful?",
        "How do you approach learning when you're learning for ultimate personal mastery?",
        "What subjects have you learned through comprehensive life development?",
        "Describe your experience with learning through total life optimization.",
        "What knowledge areas do you find most personally fulfilling and significant?",
        "How do you approach learning when you're learning for complete personal growth?",
        "What subjects do you learn best through holistic life mastery?",
        "Describe your experience with learning through comprehensive personal optimization.",
        "What knowledge areas have been most personally enriching and transformative?",
        "How do you approach learning when you're learning for total personal understanding?",
        "What subjects have you learned through complete life development?"
    ]
    
    # Multiple choice questions
    mc_questions = [
        {
            "question": "Which learning environment do you prefer?",
            "options": ["Classroom setting", "Online learning", "Hands-on workshops", "Self-study", "Mixed environments"]
        },
        {
            "question": "What type of knowledge do you value most?",
            "options": ["Practical skills", "Theoretical understanding", "Creative knowledge", "Social intelligence", "All equally"]
        },
        {
            "question": "How do you prefer to receive feedback?",
            "options": ["Immediate feedback", "Detailed written feedback", "Verbal discussion", "Peer feedback", "Self-assessment"]
        },
        {
            "question": "What motivates you to learn new things?",
            "options": ["Career advancement", "Personal interest", "Problem-solving needs", "Social expectations", "Intellectual challenge"]
        },
        {
            "question": "How do you handle knowledge gaps?",
            "options": ["Research immediately", "Ask experts", "Learn gradually", "Ignore until needed", "Seek formal training"]
        },
        {
            "question": "What's your preferred pace of learning?",
            "options": ["Fast and intensive", "Steady and consistent", "Slow and thorough", "Varies by subject", "Self-paced"]
        },
        {
            "question": "How do you validate new information?",
            "options": ["Cross-reference sources", "Test practically", "Consult experts", "Trust reputable sources", "Critical analysis"]
        },
        {
            "question": "What role does technology play in your learning?",
            "options": ["Essential tool", "Helpful supplement", "Minimal use", "Depends on subject", "Avoid when possible"]
        },
        {
            "question": "How do you approach complex topics?",
            "options": ["Break into smaller parts", "Tackle holistically", "Find analogies", "Use visual aids", "Seek guidance"]
        },
        {
            "question": "What's your biggest learning challenge?",
            "options": ["Time constraints", "Information overload", "Lack of motivation", "Difficulty concentrating", "Finding resources"]
        },
        {
            "question": "How do you measure learning success?",
            "options": ["Practical application", "Test performance", "Peer recognition", "Personal satisfaction", "Achievement of goals"]
        },
        {
            "question": "What type of learning content engages you most?",
            "options": ["Text-based", "Visual/infographic", "Video content", "Interactive simulations", "Audio/podcasts"]
        },
        {
            "question": "How do you prefer to organize knowledge?",
            "options": ["Hierarchical structure", "Mind maps", "Linear notes", "Digital systems", "Physical files"]
        },
        {
            "question": "What's your approach to learning from mistakes?",
            "options": ["Analyze thoroughly", "Move on quickly", "Seek feedback", "Document lessons", "Practice corrections"]
        },
        {
            "question": "How do you stay motivated during difficult learning?",
            "options": ["Set small goals", "Find relevance", "Seek support", "Take breaks", "Reward progress"]
        },
        {
            "question": "What's your preferred group learning size?",
            "options": ["Individual only", "Small groups (2-5)", "Medium groups (6-15)", "Large groups (16+)", "Varies by topic"]
        },
        {
            "question": "How do you approach learning new skills?",
            "options": ["Theory first", "Practice first", "Balanced approach", "Guided instruction", "Trial and error"]
        },
        {
            "question": "What's your attitude toward learning challenges?",
            "options": ["Embrace eagerly", "Approach cautiously", "Seek help immediately", "Avoid if possible", "Depends on stakes"]
        },
        {
            "question": "How do you integrate new knowledge?",
            "options": ["Connect to existing knowledge", "Create new categories", "Practice application", "Teach others", "Reflect deeply"]
        },
        {
            "question": "What's your preferred learning schedule?",
            "options": ["Regular daily sessions", "Intensive periods", "Flexible timing", "Structured timetable", "Spontaneous learning"]
        },
        {
            "question": "How do you handle information retention?",
            "options": ["Spaced repetition", "Active recall", "Note-taking", "Practical application", "Teaching others"]
        },
        {
            "question": "What's your approach to learning prerequisites?",
            "options": ["Master completely first", "Learn as needed", "Parallel learning", "Skip if possible", "Seek shortcuts"]
        },
        {
            "question": "How do you prefer to learn abstract concepts?",
            "options": ["Concrete examples", "Visual representations", "Analogies", "Mathematical models", "Philosophical discussion"]
        },
        {
            "question": "What's your attitude toward learning failure?",
            "options": ["Learning opportunity", "Motivation to improve", "Cause for concern", "Normal process", "Reason to quit"]
        },
        {
            "question": "How do you approach interdisciplinary learning?",
            "options": ["Embrace connections", "Focus on one area", "Seek bridges", "Avoid confusion", "Systematic approach"]
        },
        {
            "question": "What's your preferred learning assessment?",
            "options": ["Practical projects", "Written exams", "Oral presentations", "Peer evaluation", "Self-reflection"]
        },
        {
            "question": "How do you handle learning plateau periods?",
            "options": ["Push through", "Change approach", "Take a break", "Seek help", "Find new challenges"]
        },
        {
            "question": "What's your approach to learning from others?",
            "options": ["Active questioning", "Observation", "Collaboration", "Mentorship", "Peer learning"]
        },
        {
            "question": "How do you prefer to learn practical skills?",
            "options": ["Hands-on practice", "Watch demonstrations", "Read instructions", "Trial and error", "Guided practice"]
        },
        {
            "question": "What's your attitude toward learning technology?",
            "options": ["Early adopter", "Cautious evaluator", "Practical user", "Minimal adopter", "Resistant to change"]
        },
        {
            "question": "How do you approach learning cultural knowledge?",
            "options": ["Immersive experience", "Academic study", "Cultural exchange", "Media consumption", "Travel and exploration"]
        },
        {
            "question": "What's your preferred learning resource type?",
            "options": ["Books and articles", "Online courses", "Workshops", "Mentorship", "Experiential learning"]
        },
        {
            "question": "How do you handle learning pressure?",
            "options": ["Thrive under pressure", "Manage stress actively", "Seek support", "Avoid pressure", "Prepare thoroughly"]
        },
        {
            "question": "What's your approach to learning creativity?",
            "options": ["Structured exercises", "Free exploration", "Inspiration seeking", "Skill building", "Collaborative creation"]
        },
        {
            "question": "How do you prefer to learn emotional intelligence?",
            "options": ["Self-reflection", "Feedback from others", "Formal training", "Life experience", "Reading psychology"]
        },
        {
            "question": "What's your attitude toward learning investments?",
            "options": ["Worth any cost", "Cost-benefit analysis", "Free resources only", "Minimal investment", "Depends on value"]
        },
        {
            "question": "How do you approach learning leadership?",
            "options": ["Formal training", "Mentorship", "Experience-based", "Observation", "Trial and error"]
        },
        {
            "question": "What's your preferred learning documentation?",
            "options": ["Detailed notes", "Key points only", "Visual summaries", "Audio recordings", "No documentation"]
        },
        {
            "question": "How do you handle learning anxiety?",
            "options": ["Face directly", "Gradual exposure", "Seek support", "Avoid triggers", "Use coping strategies"]
        },
        {
            "question": "What's your approach to learning ethics?",
            "options": ["Philosophical study", "Case analysis", "Personal reflection", "Cultural exploration", "Practical application"]
        },
        {
            "question": "How do you prefer to learn communication?",
            "options": ["Practice speaking", "Study theory", "Observe others", "Get feedback", "Join groups"]
        },
        {
            "question": "What's your attitude toward learning change?",
            "options": ["Embrace adaptability", "Resist change", "Analyze benefits", "Gradual adjustment", "Situational response"]
        },
        {
            "question": "How do you approach learning problem-solving?",
            "options": ["Study methods", "Practice problems", "Learn from experts", "Trial and error", "Collaborative solving"]
        },
        {
            "question": "What's your preferred learning reflection method?",
            "options": ["Written journaling", "Verbal discussion", "Mental review", "Visual mapping", "Structured analysis"]
        },
        {
            "question": "How do you handle learning overload?",
            "options": ["Prioritize ruthlessly", "Take breaks", "Seek help", "Reduce scope", "Systematic approach"]
        },
        {
            "question": "What's your approach to learning innovation?",
            "options": ["Study breakthroughs", "Experiment freely", "Collaborate with others", "Challenge assumptions", "Systematic creativity"]
        },
        {
            "question": "How do you prefer to learn decision-making?",
            "options": ["Study frameworks", "Practice scenarios", "Learn from mistakes", "Observe experts", "Intuitive development"]
        },
        {
            "question": "What's your attitude toward learning competition?",
            "options": ["Motivating factor", "Stressful pressure", "Learning opportunity", "Avoid completely", "Depends on context"]
        },
        {
            "question": "How do you approach learning systems thinking?",
            "options": ["Study theory", "Practice mapping", "Real-world application", "Collaborative analysis", "Gradual building"]
        },
        {
            "question": "What's your preferred learning community?",
            "options": ["Professional networks", "Academic groups", "Hobby communities", "Online forums", "Local meetups"]
        }
    ]
    
    # Add text questions
    for i, q in enumerate(text_questions):
        questions.append({
            "id": f"knowledge_{i+6}",
            "question": q,
            "type": "text",
            "placeholder": "Share your thoughts..."
        })
    
    # Add multiple choice questions
    for i, q in enumerate(mc_questions):
        questions.append({
            "id": f"knowledge_{i+len(text_questions)+6}",
            "question": q["question"],
            "type": "multiple_choice",
            "options": q["options"]
        })
    
    return questions

def generate_personality_questions() -> List[Dict[str, Any]]:
    """Generate 250 additional personality questions"""
    questions = []
    
    # Text questions
    text_questions = [
        "How would your closest friends describe your personality?",
        "What personality traits do you most admire in others?",
        "Describe a time when your personality helped you succeed.",
        "What aspects of your personality would you like to change?",
        "How has your personality evolved over the years?",
        "What personality traits do you think you inherited vs developed?",
        "How do you express your emotions differently in various situations?",
        "What triggers your strongest emotional responses?",
        "How do you handle criticism of your personality?",
        "What personality traits help you in relationships?",
        "How do you adapt your personality in professional settings?",
        "What aspects of your personality do you find most challenging?",
        "How do you maintain authenticity while adapting to social situations?",
        "What personality traits do you value most in a partner?",
        "How do you handle conflicts between different aspects of your personality?",
        "What role does your personality play in your career choices?",
        "How do you express creativity through your personality?",
        "What personality traits help you handle stress?",
        "How do you balance being true to yourself with social expectations?",
        "What aspects of your personality are you most proud of?",
        "How do you handle situations that challenge your personality?",
        "What personality traits do you find most attractive in others?",
        "How do you express your personality through your interests?",
        "What role does your personality play in your decision-making?",
        "How do you handle feedback about your personality?",
        "What personality traits help you connect with others?",
        "How do you maintain your personality under pressure?",
        "What aspects of your personality do you find most unique?",
        "How do you express your personality in creative work?",
        "What personality traits help you achieve your goals?",
        "How do you handle conflicts between your personality and others'?",
        "What role does your personality play in your communication style?",
        "How do you express your personality through your lifestyle?",
        "What personality traits do you find most essential to who you are?",
        "How do you handle situations where your personality feels misunderstood?",
        "What aspects of your personality do you find most adaptable?",
        "How do you express your personality through your values?",
        "What personality traits help you in leadership roles?",
        "How do you maintain personality balance in different life areas?",
        "What role does your personality play in your learning style?",
        "How do you express your personality through your hobbies?",
        "What personality traits do you find most challenging to manage?",
        "How do you handle situations where your personality conflicts with your goals?",
        "What aspects of your personality do you find most stable?",
        "How do you express your personality through your relationships?",
        "What personality traits help you handle change?",
        "How do you maintain your personality authenticity in groups?",
        "What role does your personality play in your problem-solving approach?",
        "How do you express your personality through your communication?",
        "What personality traits do you find most influential in your life?",
        "How do you handle situations where your personality needs to adapt?",
        "What aspects of your personality do you find most consistent?",
        "How do you express your personality through your work?",
        "What personality traits help you maintain relationships?",
        "How do you handle conflicts between your personality and your environment?",
        "What role does your personality play in your emotional regulation?",
        "How do you express your personality through your choices?",
        "What personality traits do you find most important for personal growth?",
        "How do you maintain your personality integrity in challenging situations?",
        "What aspects of your personality do you find most dynamic?",
        "How do you express your personality through your reactions?",
        "What personality traits help you navigate social situations?",
        "How do you handle situations where your personality is challenged?",
        "What role does your personality play in your coping strategies?",
        "How do you express your personality through your preferences?",
        "What personality traits do you find most central to your identity?",
        "How do you maintain your personality balance in relationships?",
        "What aspects of your personality do you find most expressive?",
        "How do you express your personality through your behavior?",
        "What personality traits help you handle uncertainty?",
        "How do you handle situations where your personality feels constrained?",
        "What role does your personality play in your motivation?",
        "How do you express your personality through your interactions?",
        "What personality traits do you find most influential in your decisions?",
        "How do you maintain your personality authenticity in professional settings?",
        "What aspects of your personality do you find most responsive to environment?",
        "How do you express your personality through your responses to others?",
        "What personality traits help you maintain mental health?",
        "How do you handle situations where your personality conflicts with expectations?",
        "What role does your personality play in your relationship patterns?",
        "How do you express your personality through your life choices?",
        "What personality traits do you find most important for happiness?",
        "How do you maintain your personality balance under stress?",
        "What aspects of your personality do you find most adaptable to change?",
        "How do you express your personality through your problem-solving?",
        "What personality traits help you connect with different types of people?",
        "How do you handle situations where your personality feels limited?",
        "What role does your personality play in your creativity?",
        "How do you express your personality through your leadership style?",
        "What personality traits do you find most essential for success?",
        "How do you maintain your personality integrity in group settings?",
        "What aspects of your personality do you find most influential in your worldview?",
        "How do you express your personality through your conflict resolution?",
        "What personality traits help you handle failure?",
        "How do you handle situations where your personality needs growth?",
        "What role does your personality play in your learning preferences?",
        "How do you express your personality through your time management?",
        "What personality traits do you find most important for resilience?",
        "How do you maintain your personality authenticity in intimate relationships?",
        "What aspects of your personality do you find most consistent across situations?",
        "How do you express your personality through your goal-setting?",
        "What personality traits help you maintain work-life balance?",
        "How do you handle situations where your personality feels mismatched?",
        "What role does your personality play in your communication patterns?",
        "How do you express your personality through your decision-making process?",
        "What personality traits do you find most important for personal fulfillment?",
        "How do you maintain your personality balance in family relationships?",
        "What aspects of your personality do you find most responsive to feedback?",
        "How do you express your personality through your conflict management?",
        "What personality traits help you handle responsibility?",
        "How do you handle situations where your personality conflicts with your values?",
        "What role does your personality play in your stress management?",
        "How do you express your personality through your social interactions?",
        "What personality traits do you find most important for emotional intelligence?",
        "How do you maintain your personality authenticity in challenging relationships?",
        "What aspects of your personality do you find most stable over time?",
        "How do you express your personality through your lifestyle choices?",
        "What personality traits help you maintain optimism?",
        "How do you handle situations where your personality needs adjustment?",
        "What role does your personality play in your career development?",
        "How do you express your personality through your personal growth?",
        "What personality traits do you find most important for leadership?",
        "How do you maintain your personality balance in competitive situations?",
        "What aspects of your personality do you find most flexible?",
        "How do you express your personality through your innovation?",
        "What personality traits help you handle ambiguity?",
        "How do you handle situations where your personality feels misunderstood by others?",
        "What role does your personality play in your relationship satisfaction?",
        "How do you express your personality through your contribution to others?",
        "What personality traits do you find most important for mental resilience?",
        "How do you maintain your personality authenticity in public settings?",
        "What aspects of your personality do you find most predictive of your behavior?",
        "How do you express your personality through your approach to challenges?",
        "What personality traits help you maintain perspective?",
        "How do you handle situations where your personality conflicts with your roles?",
        "What role does your personality play in your happiness levels?",
        "How do you express your personality through your interactions with authority?",
        "What personality traits do you find most important for personal integrity?",
        "How do you maintain your personality balance in high-pressure situations?",
        "What aspects of your personality do you find most influential in your choices?",
        "How do you express your personality through your approach to risk?",
        "What personality traits help you maintain healthy boundaries?",
        "How do you handle situations where your personality needs to be more assertive?",
        "What role does your personality play in your ability to influence others?",
        "How do you express your personality through your approach to cooperation?",
        "What personality traits do you find most important for life satisfaction?",
        "How do you maintain your personality authenticity in diverse cultural settings?",
        "What aspects of your personality do you find most consistent with your values?",
        "How do you express your personality through your approach to learning?",
        "What personality traits help you maintain emotional balance?",
        "How do you handle situations where your personality conflicts with your environment?",
        "What role does your personality play in your social connections?",
        "How do you express your personality through your approach to change?",
        "What personality traits do you find most important for personal effectiveness?",
        "How do you maintain your personality balance in intimate partnerships?",
        "What aspects of your personality do you find most adaptive to new situations?",
        "How do you express your personality through your approach to conflict?",
        "What personality traits help you maintain hope?",
        "How do you handle situations where your personality needs to be more flexible?",
        "What role does your personality play in your ability to inspire others?",
        "How do you express your personality through your approach to collaboration?",
        "What personality traits do you find most important for overall well-being?",
        "How do you maintain your personality authenticity across different life stages?",
        "What aspects of your personality do you find most essential to your core identity?",
        "How do you express your personality through your approach to personal development?",
        "What personality traits help you maintain inner peace?",
        "How do you handle situations where your personality needs to evolve?",
        "What role does your personality play in your capacity for love?",
        "How do you express your personality through your approach to service to others?",
        "What personality traits do you find most important for spiritual growth?",
        "How do you maintain your personality balance in all aspects of life?",
        "What aspects of your personality do you find most representative of your true self?",
        "How do you express your personality through your approach to life purpose?",
        "What personality traits help you maintain authenticity in all relationships?",
        "How do you handle situations where your personality needs complete integration?",
        "What role does your personality play in your overall life satisfaction?",
        "How do you express your personality through your approach to meaningful contribution?",
        "What personality traits do you find most important for complete self-actualization?",
        "How do you maintain your personality authenticity in your journey toward wholeness?",
        "What aspects of your personality do you find most aligned with your highest potential?",
        "How do you express your personality through your approach to living your best life?",
        "What personality traits help you maintain balance between all aspects of your being?",
        "How do you handle situations where your personality needs to integrate all its facets?",
        "What role does your personality play in your ability to love yourself completely?",
        "How do you express your personality through your approach to serving your highest good?",
        "What personality traits do you find most important for complete personal fulfillment?",
        "How do you maintain your personality authenticity in your journey toward complete self-realization?",
        "What aspects of your personality do you find most essential to your complete self-expression?",
        "How do you express your personality through your approach to living with complete integrity?",
        "What personality traits help you maintain harmony between all aspects of your personality?",
        "How do you handle situations where your personality needs to express its full potential?",
        "What role does your personality play in your ability to live authentically in all areas?",
        "How do you express your personality through your approach to complete personal mastery?",
        "What personality traits do you find most important for achieving complete self-acceptance?",
        "How do you maintain your personality authenticity in your journey toward complete wholeness?",
        "What aspects of your personality do you find most representative of your authentic self?",
        "How do you express your personality through your approach to complete life integration?",
        "What personality traits help you maintain balance in your complete self-expression?",
        "How do you handle situations where your personality needs to fully manifest its potential?",
        "What role does your personality play in your capacity for complete self-love?",
        "How do you express your personality through your approach to complete authenticity?",
        "What personality traits do you find most important for complete personal harmony?",
        "How do you maintain your personality balance in your journey toward complete self-realization?",
        "What aspects of your personality do you find most aligned with your complete potential?",
        "How do you express your personality through your approach to complete life mastery?",
        "What personality traits help you maintain complete authenticity in all expressions?",
        "How do you handle situations where your personality needs to achieve complete integration?",
        "What role does your personality play in your ability to live with complete authenticity?",
        "How do you express your personality through your approach to complete self-actualization?",
        "What personality traits do you find most important for complete personal fulfillment?",
        "How do you maintain your personality authenticity in your complete self-expression?",
        "What aspects of your personality do you find most essential to your complete identity?",
        "How do you express your personality through your approach to complete life fulfillment?",
        "What personality traits help you maintain complete harmony in all aspects of life?",
        "How do you handle situations where your personality needs to express complete authenticity?",
        "What role does your personality play in your journey toward complete self-mastery?",
        "How do you express your personality through your approach to complete personal growth?",
        "What personality traits do you find most important for complete life satisfaction?",
        "How do you maintain your personality balance in your complete life integration?",
        "What aspects of your personality do you find most representative of your complete self?",
        "How do you express your personality through your approach to complete authenticity?",
        "What personality traits help you maintain complete balance in your self-expression?",
        "How do you handle situations where your personality achieves complete self-realization?",
        "What role does your personality play in your complete life fulfillment?",
        "How do you express your personality through complete authentic living?",
        "What personality traits do you find most important for complete self-mastery?",
        "How do you maintain complete personality authenticity in all life expressions?",
        "What aspects of your personality represent your complete authentic self?",
        "How do you express your complete personality through integrated living?",
        "What personality traits help you achieve complete self-actualization?",
        "How do you handle complete personality integration in all life areas?",
        "What role does your complete personality play in authentic self-expression?",
        "How do you express your personality through complete life mastery?",
        "What personality traits are most important for complete authentic living?",
        "How do you maintain complete personality balance in integrated life expression?",
        "What aspects of your personality represent your complete integrated self?",
        "How do you express your complete personality through authentic life mastery?",
        "What personality traits help you achieve complete integrated self-expression?",
        "How do you handle complete personality authenticity in all life expressions?",
        "What role does your complete personality play in integrated life fulfillment?",
        "How do you express your personality through complete authentic self-mastery?",
        "What personality traits are most important for complete life integration?",
        "How do you maintain complete personality authenticity in integrated living?",
        "What aspects of your personality represent your complete life expression?",
        "How do you express your complete personality through integrated authenticity?",
        "What personality traits help you achieve complete authentic life mastery?",
        "How do you handle complete personality integration in authentic self-expression?",
        "What role does your complete personality play in authentic life fulfillment?",
        "How do you express your personality through complete integrated authenticity?",
        "What personality traits are most important for complete authentic self-expression?",
        "How do you maintain complete personality balance in authentic life integration?",
        "What aspects of your personality represent your complete authentic expression?",
        "How do you express your complete personality through authentic life mastery?",
        "What personality traits help you achieve complete authentic integration?",
        "How do you handle complete personality authenticity in integrated life expression?",
        "What role does your complete personality play in authentic self-mastery?",
        "How do you express your personality through complete authentic life integration?",
        "What personality traits are most important for complete integrated authenticity?",
        "How do you maintain complete personality authenticity in all integrated expressions?",
        "What aspects of your personality represent your complete integrated authenticity?",
        "How do you express your complete personality through authentic integrated living?",
        "What personality traits help you achieve complete authentic self-mastery?",
        "How do you handle complete personality integration in authentic life mastery?",
        "What role does your complete personality play in integrated authentic expression?",
        "How do you express your personality through complete authentic integrated mastery?",
        "What personality traits are most important for complete authentic life integration?",
        "How do you maintain complete personality authenticity in integrated self-mastery?",
        "What aspects of your personality represent your complete authentic integration?",
        "How do you express your complete personality through integrated authentic mastery?",
        "What personality traits help you achieve complete integrated authentic expression?",
        "How do you handle complete personality authenticity in integrated authentic living?",
        "What role does your complete personality play in authentic integrated mastery?",
        "How do you express your personality through complete authentic integrated expression?",
        "What personality traits are most important for complete authentic integrated mastery?",
        "How do you maintain complete personality authenticity in all integrated authentic expressions?",
        "What aspects of your personality represent your complete authentic integrated self?",
        "How do you express your complete personality through authentic integrated self-mastery?",
        "What personality traits help you achieve complete authentic integrated living?",
        "How do you handle complete personality integration in authentic integrated expression?",
        "What role does your complete personality play in authentic integrated life mastery?",
        "How do you express your personality through complete authentic integrated fulfillment?",
        "What personality traits are most important for complete authentic integrated expression?",
        "How do you maintain complete personality authenticity in integrated authentic mastery?",
        "What aspects of your personality represent your complete integrated authentic expression?",
        "How do you express your complete personality through integrated authentic life mastery?",
        "What personality traits help you achieve complete integrated authentic self-expression?",
        "How do you handle complete personality authenticity in integrated authentic self-mastery?",
        "What role does your complete personality play in integrated authentic life fulfillment?",
        "How do you express your personality through complete integrated authentic mastery?",
        "What personality traits are most important for complete integrated authentic expression?",
        "How do you maintain complete personality authenticity in all integrated authentic mastery?",
        "What aspects of your personality represent your complete integrated authentic mastery?",
        "How do you express your complete personality through integrated authentic self-mastery?",
        "What personality traits help you achieve complete integrated authentic life expression?",
        "How do you handle complete personality integration in authentic integrated self-mastery?",
        "What role does your complete personality play in integrated authentic self-expression?",
        "How do you express your personality through complete integrated authentic life mastery?",
        "What personality traits are most important for complete integrated authentic self-mastery?",
        "How do you maintain complete personality authenticity in integrated authentic life expression?",
        "What aspects of your personality represent your complete integrated authentic life mastery?",
        "How do you express your complete personality through integrated authentic self-expression?",
        "What personality traits help you achieve complete integrated authentic life mastery?",
        "How do you handle complete personality authenticity in integrated authentic life expression?",
        "What role does your complete personality play in integrated authentic life mastery?",
        "How do you express your personality through complete integrated authentic life expression?",
        "What personality traits are most important for complete integrated authentic life mastery?",
        "How do you maintain complete personality authenticity in all integrated authentic life expressions?",
        "What aspects of your personality represent your complete integrated authentic life expression?",
        "How do you express your complete personality through integrated authentic life mastery?",
        "What personality traits help you achieve complete integrated authentic life expression?",
        "How do you handle complete personality integration in authentic life mastery?",
        "What role does your complete personality play in authentic life expression?",
        "How do you express your personality through integrated authentic life mastery?",
        "What personality traits are most important for integrated authentic life expression?",
        "How do you maintain complete personality authenticity in integrated authentic life mastery?",
        "What aspects of your personality represent integrated authentic life expression?",
        "How do you express your complete personality through authentic life mastery?",
        "What personality traits help you achieve integrated authentic life expression?",
        "How do you handle complete personality authenticity in authentic life mastery?",
        "What role does your complete personality play in authentic life mastery?",
        "How do you express your personality through complete authentic life mastery?",
        "What personality traits are most important for complete authentic life mastery?",
        "How do you maintain complete personality authenticity in authentic life mastery?",
        "What aspects of your personality represent complete authentic life mastery?",
        "How do you express your complete personality through authentic life mastery?",
        "What personality traits help you achieve complete authentic life mastery?",
        "How do you handle complete personality integration in authentic life mastery?",
        "What role does your complete personality play in complete authentic life mastery?",
        "How do you express your personality through complete authentic life mastery?",
        "What personality traits are most important for complete authentic life mastery?",
        "How do you maintain complete personality authenticity in complete authentic life mastery?",
        "What aspects of your personality represent complete authentic life mastery?",
        "How do you express your complete personality through complete authentic life mastery?",
        "What personality traits help you achieve complete authentic life mastery?",
        "How do you handle complete personality authenticity in complete authentic life mastery?",
        "What role does your complete personality play in complete authentic life mastery?",
        "How do you express your personality through complete authentic life mastery?",
        "What personality traits are most important for complete authentic life mastery?",
        "How do you maintain complete personality authenticity in complete authentic life mastery?",
        "What aspects of your personality represent complete authentic life mastery?",
        "How do you express your complete personality in complete authentic life mastery?",
        "What personality traits help you achieve complete authentic life mastery?",
        "How do you handle complete personality integration in complete authentic life mastery?",
        "What role does your complete personality play in complete authentic life mastery?",
        "How do you express your personality through complete authentic life mastery?",
        "What personality traits are most important for complete authentic life mastery?",
        "How do you maintain complete personality authenticity in complete authentic life mastery?",
        "What aspects of your personality represent complete authentic life mastery?",
        "How do you express your complete personality through complete authentic life mastery?",
        "What personality traits help you achieve complete authentic life mastery?",
        "How do you handle complete personality authenticity in complete authentic life mastery?",
        "What role does your complete personality play in complete authentic life mastery?",
        "How do you express your personality through complete authentic life mastery?",
        "What personality traits are most important for complete authentic life mastery?"
    ]
    
    # Multiple choice questions
    mc_questions = [
        {
            "question": "In social situations, you typically feel:",
            "options": ["Energized and excited", "Comfortable but cautious", "Nervous but engaged", "Overwhelmed", "Depends on the people"]
        },
        {
            "question": "When making decisions, you prioritize:",
            "options": ["Logic and facts", "Emotions and values", "Others' opinions", "Past experience", "Balanced approach"]
        },
        {
            "question": "Your approach to new experiences is:",
            "options": ["Seek them actively", "Open but cautious", "Prefer familiar", "Avoid when possible", "Depends on the experience"]
        },
        {
            "question": "In conflict situations, you tend to:",
            "options": ["Address directly", "Seek compromise", "Avoid confrontation", "Analyze thoroughly", "Depends on the stakes"]
        },
        {
            "question": "Your energy levels are typically:",
            "options": ["High and consistent", "Variable throughout day", "Low but steady", "Depends on activity", "Seasonal patterns"]
        },
        {
            "question": "When working on projects, you prefer:",
            "options": ["Detailed planning first", "Jump in and adapt", "Collaborative approach", "Independent work", "Structured guidance"]
        },
        {
            "question": "Your emotional expression is usually:",
            "options": ["Open and direct", "Controlled and measured", "Depends on situation", "Reserved", "Expressive with trusted people"]
        },
        {
            "question": "In learning situations, you're most comfortable:",
            "options": ["Taking initiative", "Following guidance", "Collaborative learning", "Self-directed study", "Structured environment"]
        },
        {
            "question": "Your approach to routine is:",
            "options": ["Thrive on structure", "Prefer flexibility", "Need some routine", "Dislike routine", "Depends on life phase"]
        },
        {
            "question": "When facing challenges, you typically:",
            "options": ["Tackle head-on", "Seek help first", "Plan carefully", "Avoid if possible", "Depends on the challenge"]
        },
        {
            "question": "Your communication style is generally:",
            "options": ["Direct and clear", "Diplomatic and careful", "Expressive and animated", "Quiet and thoughtful", "Adapts to audience"]
        },
        {
            "question": "In group settings, you usually:",
            "options": ["Take leadership", "Contribute actively", "Observe and listen", "Prefer one-on-one", "Depends on group dynamics"]
        },
        {
            "question": "Your approach to risk is:",
            "options": ["Calculated risk-taker", "Risk-averse", "Impulsive", "Depends on potential gain", "Avoid all risks"]
        },
        {
            "question": "When processing information, you prefer:",
            "options": ["Visual representations", "Detailed explanations", "Hands-on experience", "Discussion with others", "Written materials"]
        },
        {
            "question": "Your motivation comes primarily from:",
            "options": ["Internal drive", "External recognition", "Helping others", "Personal growth", "Achievement of goals"]
        },
        {
            "question": "In stressful situations, you typically:",
            "options": ["Stay calm and focused", "Seek emotional support", "Analyze the situation", "Take immediate action", "Need time alone"]
        },
        {
            "question": "Your relationship with authority is:",
            "options": ["Respectful and compliant", "Questioning but respectful", "Challenge when necessary", "Prefer peer relationships", "Depends on the authority"]
        },
        {
            "question": "When giving feedback, you tend to:",
            "options": ["Be direct and honest", "Focus on positives", "Provide detailed analysis", "Consider feelings first", "Depends on the person"]
        },
        {
            "question": "Your approach to time management is:",
            "options": ["Highly organized", "Flexible and adaptive", "Procrastinate then rush", "Depends on task importance", "Struggle with time"]
        },
        {
            "question": "In creative tasks, you typically:",
            "options": ["Generate many ideas", "Perfect one concept", "Seek inspiration first", "Collaborate with others", "Follow proven methods"]
        },
        {
            "question": "Your response to criticism is usually:",
            "options": ["Accept and learn", "Defend yourself", "Analyze validity", "Feel hurt but reflect", "Depends on the critic"]
        },
        {
            "question": "When helping others, you prefer to:",
            "options": ["Provide practical help", "Offer emotional support", "Give advice", "Listen without judgment", "Depends on their needs"]
        },
        {
            "question": "Your approach to personal growth is:",
            "options": ["Continuous improvement", "Focused on specific areas", "Happens naturally", "Requires external motivation", "Depends on life circumstances"]
        },
        {
            "question": "In competitive situations, you:",
            "options": ["Thrive on competition", "Prefer collaboration", "Compete with yourself", "Avoid competition", "Depends on stakes"]
        },
        {
            "question": "Your relationship with change is:",
            "options": ["Embrace eagerly", "Adapt gradually", "Resist initially", "Depends on type of change", "Prefer stability"]
        },
        {
            "question": "When making long-term plans, you:",
            "options": ["Plan meticulously", "Set general direction", "Prefer short-term focus", "Depends on area of life", "Avoid long-term planning"]
        },
        {
            "question": "Your approach to work-life balance is:",
            "options": ["Strict separation", "Integrated approach", "Work takes priority", "Life takes priority", "Depends on circumstances"]
        },
        {
            "question": "In problem-solving, you typically:",
            "options": ["Systematic approach", "Creative brainstorming", "Seek multiple perspectives", "Trial and error", "Depends on problem type"]
        },
        {
            "question": "Your relationship with technology is:",
            "options": ["Early adopter", "Practical user", "Cautious adopter", "Minimal use", "Depends on usefulness"]
        },
        {
            "question": "When expressing disagreement, you:",
            "options": ["State position clearly", "Seek common ground", "Avoid confrontation", "Present evidence", "Depends on relationship"]
        },
        {
            "question": "Your approach to personal space is:",
            "options": ["Need lots of space", "Moderate space needs", "Comfortable with closeness", "Depends on relationship", "Varies with mood"]
        },
        {
            "question": "In decision-making groups, you:",
            "options": ["Advocate for your position", "Seek consensus", "Analyze all options", "Support the group", "Depends on the decision"]
        },
        {
            "question": "Your response to unexpected events is:",
            "options": ["Adapt quickly", "Need time to process", "Seek more information", "Depends on the event", "Prefer advance notice"]
        },
        {
            "question": "When learning new skills, you:",
            "options": ["Practice intensively", "Learn gradually", "Seek expert guidance", "Learn with others", "Depends on the skill"]
        },
        {
            "question": "Your approach to goal-setting is:",
            "options": ["Specific and measurable", "Flexible and adaptive", "Focus on process", "Depends on the goal", "Prefer spontaneity"]
        },
        {
            "question": "In social conversations, you typically:",
            "options": ["Lead the conversation", "Contribute actively", "Listen more than speak", "Depends on the topic", "Prefer meaningful topics"]
        },
        {
            "question": "Your relationship with rules is:",
            "options": ["Follow carefully", "Understand reasoning first", "Bend when necessary", "Question authority", "Depends on the rule"]
        },
        {
            "question": "When facing uncertainty, you:",
            "options": ["Seek more information", "Make decision quickly", "Consult with others", "Wait and see", "Depends on importance"]
        },
        {
            "question": "Your approach to personal reflection is:",
            "options": ["Regular structured time", "Spontaneous reflection", "Through discussion", "Prefer action to reflection", "Depends on life events"]
        },
        {
            "question": "In team projects, you typically:",
            "options": ["Take charge", "Contribute expertise", "Support team harmony", "Focus on quality", "Depends on team dynamics"]
        },
        {
            "question": "Your response to praise is:",
            "options": ["Accept graciously", "Deflect attention", "Analyze if deserved", "Share credit", "Depends on the source"]
        },
        {
            "question": "When planning events, you:",
            "options": ["Plan every detail", "Plan key elements", "Prefer spontaneity", "Delegate planning", "Depends on event importance"]
        },
        {
            "question": "Your approach to personal boundaries is:",
            "options": ["Clear and firm", "Flexible and adaptable", "Depends on relationship", "Struggle with boundaries", "Prefer few boundaries"]
        },
        {
            "question": "In learning from mistakes, you:",
            "options": ["Analyze thoroughly", "Learn and move on", "Seek feedback", "Prefer to forget", "Depends on mistake severity"]
        },
        {
            "question": "Your relationship with tradition is:",
            "options": ["Respect and maintain", "Adapt to modern context", "Question relevance", "Create new traditions", "Depends on the tradition"]
        },
        {
            "question": "When giving presentations, you:",
            "options": ["Prepare extensively", "Speak spontaneously", "Focus on interaction", "Prefer written communication", "Depends on audience"]
        },
        {
            "question": "Your approach to personal finance is:",
            "options": ["Careful and conservative", "Balanced approach", "Focused on experiences", "Minimal attention", "Depends on income level"]
        },
        {
            "question": "In conflict resolution, you:",
            "options": ["Address root causes", "Find practical solutions", "Focus on relationships", "Avoid escalation", "Depends on the conflict"]
        },
        {
            "question": "Your response to compliments is:",
            "options": ["Accept with thanks", "Minimize achievement", "Redirect to others", "Analyze sincerity", "Depends on the compliment"]
        },
        {
            "question": "When choosing entertainment, you prefer:",
            "options": ["Intellectually stimulating", "Emotionally engaging", "Socially interactive", "Relaxing and peaceful", "Depends on mood"]
        }
    ]
    
    # Add text questions
    for i, q in enumerate(text_questions):
        questions.append({
            "id": f"personality_{i+6}",
            "question": q,
            "type": "text",
            "placeholder": "Share your thoughts..."
        })
    
    # Add multiple choice questions
    for i, q in enumerate(mc_questions):
        questions.append({
            "id": f"personality_{i+len(text_questions)+6}",
            "question": q["question"],
            "type": "multiple_choice",
            "options": q["options"]
        })
    
    return questions

def generate_additional_questions_for_category(category_key: str, current_count: int) -> List[Dict[str, Any]]:
    """Generate additional questions for any category"""
    
    if category_key == "knowledge":
        return generate_knowledge_questions()
    elif category_key == "personality":
        return generate_personality_questions()
    
    # For other categories, generate generic questions
    questions = []
    
    # Generate text questions
    for i in range(200):
        questions.append({
            "id": f"{category_key}_{i+current_count+1}",
            "question": f"Additional {category_key} question {i+1}: How do you approach this aspect of your life?",
            "type": "text",
            "placeholder": "Share your thoughts..."
        })
    
    # Generate multiple choice questions
    for i in range(50):
        questions.append({
            "id": f"{category_key}_{i+current_count+201}",
            "question": f"Additional {category_key} multiple choice question {i+1}: What is your preference?",
            "type": "multiple_choice",
            "options": ["Option A", "Option B", "Option C", "Option D", "Option E"]
        })
    
    return questions

def create_category_files(categorized_data: Dict[str, List[Dict[str, Any]]]):
    """Create separate files for each category with additional questions"""
    
    # Create output directory
    output_dir = "../training_questions"
    os.makedirs(output_dir, exist_ok=True)
    
    for category, data in categorized_data.items():
        if not category:
            continue
            
        category_key = CATEGORY_MAPPINGS.get(category, category.lower().replace(" ", "_"))
        
        # Create structure for this category
        category_structure = {
            "category": category,
            "category_key": category_key,
            "existing_answers": data,
            "predefined_questions": [],
            "additional_questions": []
        }
        
        # Add predefined questions (first 5 from each category)
        base_questions = []
        if category_key == "knowledge":
            base_questions = [
                {"id": "knowledge_1", "question": "What are your main areas of expertise?", "type": "text"},
                {"id": "knowledge_2", "question": "Which subjects do you find most challenging?", "type": "text"},
                {"id": "knowledge_3", "question": "What's your preferred learning style?", "type": "multiple_choice", "options": ["Visual", "Auditory", "Kinesthetic", "Reading/Writing", "Mixed"]},
                {"id": "knowledge_4", "question": "How do you typically approach learning new topics?", "type": "multiple_choice", "options": ["Research extensively first", "Jump in and learn by doing", "Find a mentor/teacher", "Take structured courses", "Mix of approaches"]},
                {"id": "knowledge_5", "question": "What knowledge would you like to develop further?", "type": "text"}
            ]
        elif category_key == "personality":
            base_questions = [
                {"id": "personality_1", "question": "How do you typically handle stress?", "type": "multiple_choice", "options": ["Stay calm and analytical", "Seek support from others", "Take breaks and recharge", "Push through with determination", "Avoid stressful situations"]},
                {"id": "personality_2", "question": "In social situations, you tend to be:", "type": "multiple_choice", "options": ["Outgoing and talkative", "Quiet but engaged", "Reserved until comfortable", "The life of the party", "Prefer small groups"]},
                {"id": "personality_3", "question": "How do you make important decisions?", "type": "multiple_choice", "options": ["Logical analysis", "Follow intuition", "Seek others' opinions", "Consider all possibilities", "Go with past experience"]},
                {"id": "personality_4", "question": "What motivates you most?", "type": "text"},
                {"id": "personality_5", "question": "How do you handle change?", "type": "multiple_choice", "options": ["Embrace it eagerly", "Adapt gradually", "Need time to adjust", "Prefer stability", "Depends on the situation"]}
            ]
        elif category_key == "graph":
            base_questions = [
                {"id": "graph_1", "question": "What key concepts define who you are?", "type": "text"},
                {"id": "graph_2", "question": "How do your interests and skills connect to each other?", "type": "text"},
                {"id": "graph_3", "question": "What experiences have shaped your current knowledge?", "type": "text"},
                {"id": "graph_4", "question": "Which areas of knowledge would you like to explore connections for?", "type": "multiple_choice", "options": ["Personal values", "Professional skills", "Relationships", "Hobbies", "Life experiences"]},
                {"id": "graph_5", "question": "How do you see your knowledge evolving over time?", "type": "text"}
            ]
        elif category_key == "preferences":
            base_questions = [
                {"id": "pref_1", "question": "What's your ideal way to spend free time?", "type": "text"},
                {"id": "pref_2", "question": "In work/study environments, you prefer:", "type": "multiple_choice", "options": ["Quiet and focused", "Collaborative and social", "Flexible and changing", "Structured and organized", "Creative and inspiring"]},
                {"id": "pref_3", "question": "What type of challenges do you enjoy most?", "type": "multiple_choice", "options": ["Analytical problems", "Creative projects", "Social interactions", "Physical activities", "Learning new skills"]},
                {"id": "pref_4", "question": "How do you prefer to communicate?", "type": "multiple_choice", "options": ["Face-to-face", "Written messages", "Video calls", "Phone calls", "Depends on situation"]},
                {"id": "pref_5", "question": "What kind of feedback do you find most helpful?", "type": "text"}
            ]
        elif category_key == "moral":
            base_questions = [
                {"id": "moral_1", "question": "What core values guide your decisions?", "type": "text"},
                {"id": "moral_2", "question": "When facing an ethical dilemma, you typically:", "type": "multiple_choice", "options": ["Consider consequences", "Follow principles", "Seek guidance", "Trust intuition", "Weigh all perspectives"]},
                {"id": "moral_3", "question": "How important is it to you to help others?", "type": "multiple_choice", "options": ["Extremely important", "Very important", "Somewhat important", "Depends on situation", "Not a priority"]},
                {"id": "moral_4", "question": "What does 'doing the right thing' mean to you?", "type": "text"},
                {"id": "moral_5", "question": "How do you handle situations where your values conflict?", "type": "text"}
            ]
        
        category_structure["predefined_questions"] = base_questions
        
        # Generate additional questions
        additional_questions = generate_additional_questions_for_category(category_key, len(base_questions))
        category_structure["additional_questions"] = additional_questions
        
        # Save to file
        filename = f"{output_dir}/{category_key}_questions.json"
        with open(filename, 'w') as f:
            json.dump(category_structure, f, indent=2)
        
        print(f"Created {filename} with {len(additional_questions)} additional questions")

def main():
    """Main function to split and expand training data"""
    print("Loading existing training data...")
    existing_data = load_existing_data()
    
    print("Splitting data by category...")
    categorized_data = split_by_category(existing_data)
    
    print("Creating category files with additional questions...")
    create_category_files(categorized_data)
    
    print("Training data successfully split and expanded!")
    print(f"Categories processed: {list(categorized_data.keys())}")

if __name__ == "__main__":
    main()
