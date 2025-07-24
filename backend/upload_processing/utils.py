"""
Utility functions for document upload processing

This module contains utility functions used throughout the document analysis system.
"""

import logging
import json
import re
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import mimetypes
from datetime import datetime

logger = logging.getLogger(__name__)

async def get_file_content(document_info: Dict[str, Any]) -> Optional[str]:
    """
    Get file content from MongoDB or local storage
    
    Args:
        document_info: Document information dictionary
        
    Returns:
        File content as string or None if not found/not readable
    """
    try:
        # Import here to avoid circular imports - use robust approach
        import sys
        import importlib
        
        # Try to get the already-loaded main module first
        main_mod = sys.modules.get("main")
        
        # If not found, attempt to import it using common module paths
        if main_mod is None:
            try:
                main_mod = importlib.import_module("main")
            except ImportError:
                try:
                    main_mod = importlib.import_module("Model_Myself.backend.main")
                except ImportError:
                    main_mod = None
        
        if main_mod:
            mongodb_connected = getattr(main_mod, "mongodb_connected", False)
            database = getattr(main_mod, "database", None)
            fs_bucket = getattr(main_mod, "fs_bucket", None)
        else:
            mongodb_connected = False
            database = None
            fs_bucket = None
        
        logger.debug(f"get_file_content - MongoDB connected: {mongodb_connected}")
        
        if mongodb_connected and fs_bucket is not None:
            # Get from MongoDB GridFS
            file_id = document_info.get("file_id")
            logger.debug(f"Attempting to retrieve file with ID: {file_id}")
            if file_id:
                try:
                    grid_out = await fs_bucket.open_download_stream(file_id)
                    content_bytes = await grid_out.read()
                    logger.debug(f"Retrieved {len(content_bytes)} bytes from GridFS")
                    
                    # Try to decode as text
                    try:
                        return content_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        # Try other encodings
                        for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                            try:
                                return content_bytes.decode(encoding)
                            except UnicodeDecodeError:
                                continue
                        logger.warning(f"Could not decode content for file {document_info.get('filename')}")
                        return None
                except Exception as e:
                    logger.error(f"Error retrieving file from GridFS: {e}")
                    return None
            else:
                logger.warning(f"No file_id found in document_info for {document_info.get('filename')}")
        else:
            # Get from local storage
            local_path = document_info.get("local_path")
            if local_path:
                file_path = Path(local_path)
                # If the path is relative and doesn't exist, try resolving relative to backend package
                if not file_path.exists():
                    file_path = (Path(__file__).resolve().parent.parent / file_path).resolve()
                if file_path.exists():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            return f.read()
                    except UnicodeDecodeError:
                        # Try other encodings
                        for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                            try:
                                with open(file_path, 'r', encoding=encoding) as f:
                                    return f.read()
                            except UnicodeDecodeError:
                                continue
                        logger.warning(f"Could not decode content for file {file_path}")
                        return None
    
    except Exception as e:
        logger.error(f"Error getting file content: {e}")
        return None
    
    return None

def detect_language(text: str) -> str:
    """
    Detect the language of given text
    
    Args:
        text: Input text
        
    Returns:
        Language code (e.g., 'en', 'es', 'fr') or 'unknown'
    """
    if not text or len(text.strip()) < 10:
        return "unknown"
    
    # Simple language detection based on common words
    # In a real implementation, you'd use a library like langdetect
    
    text_lower = text.lower()
    
    # English indicators
    english_words = ['the', 'and', 'that', 'have', 'for', 'not', 'with', 'you', 'this', 'but']
    english_score = sum(1 for word in english_words if word in text_lower)
    
    # Spanish indicators
    spanish_words = ['que', 'de', 'la', 'el', 'en', 'y', 'a', 'un', 'es', 'con']
    spanish_score = sum(1 for word in spanish_words if word in text_lower)
    
    # French indicators
    french_words = ['le', 'de', 'et', 'un', 'à', 'il', 'être', 'et', 'en', 'avoir']
    french_score = sum(1 for word in french_words if word in text_lower)
    
    # German indicators
    german_words = ['der', 'die', 'und', 'in', 'den', 'zu', 'das', 'mit', 'ich', 'ist']
    german_score = sum(1 for word in german_words if word in text_lower)
    
    scores = {
        'en': english_score,
        'es': spanish_score,
        'fr': french_score,
        'de': german_score
    }
    
    max_score = max(scores.values())
    if max_score == 0:
        return "unknown"
    
    return max(scores, key=scores.get)

def clean_text(text: str, remove_extra_whitespace: bool = True, remove_special_chars: bool = False) -> str:
    """
    Clean text for processing
    
    Args:
        text: Input text
        remove_extra_whitespace: Whether to remove extra whitespace
        remove_special_chars: Whether to remove special characters
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    cleaned = text
    
    if remove_extra_whitespace:
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()
    
    if remove_special_chars:
        # Remove special characters, keep only letters, numbers, and basic punctuation
        cleaned = re.sub(r'[^\w\s.,!?;:()-]', '', cleaned)
    
    return cleaned

def validate_document_format(file_type: str, analysis_type: str) -> bool:
    """
    Validate if a document format is supported for a specific analysis type
    
    Args:
        file_type: MIME type of the file
        analysis_type: Type of analysis to perform
        
    Returns:
        True if format is supported, False otherwise
    """
    # Define supported formats for each analysis type
    format_support = {
        "text_extraction": [
            "text/plain", "text/markdown", "text/html", "application/json",
            "text/csv", "application/xml", "text/xml"
        ],
        "sentiment": [
            "text/plain", "text/markdown", "text/html", "application/json"
        ],
        "keywords": [
            "text/plain", "text/markdown", "text/html", "application/json", 
            "text/csv"
        ],
        "summary": [
            "text/plain", "text/markdown", "text/html", "application/json"
        ],
        "metadata": [
            "all"  # Metadata can be extracted from any format
        ]
    }
    
    supported_formats = format_support.get(analysis_type, [])
    
    if "all" in supported_formats:
        return True
    
    # Normalize file type
    file_type = file_type.lower()
    
    # Check direct match
    if file_type in supported_formats:
        return True
    
    # Check for partial matches (e.g., "text/" prefix)
    for supported_format in supported_formats:
        if supported_format.endswith("/") and file_type.startswith(supported_format):
            return True
    
    return False

def extract_text_from_html(html_content: str) -> str:
    """
    Extract text from HTML content
    
    Args:
        html_content: HTML content string
        
    Returns:
        Extracted text
    """
    # Simple HTML tag removal
    # In a real implementation, you'd use BeautifulSoup or similar
    
    # Remove script and style elements
    html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', html_content)
    
    # Decode HTML entities
    html_entities = {
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'",
        '&nbsp;': ' ',
        '&copy;': '©',
        '&reg;': '®',
        '&trade;': '™'
    }
    
    for entity, char in html_entities.items():
        text = text.replace(entity, char)
    
    return clean_text(text)

def extract_text_from_json(json_content: str) -> str:
    """
    Extract text from JSON content
    
    Args:
        json_content: JSON content string
        
    Returns:
        Extracted text
    """
    try:
        data = json.loads(json_content)
        return _extract_text_from_json_object(data)
    except json.JSONDecodeError:
        logger.warning("Invalid JSON content")
        return json_content  # Return as-is if not valid JSON

def _extract_text_from_json_object(obj: Union[Dict, List, str, int, float, bool, None]) -> str:
    """
    Recursively extract text from JSON object
    
    Args:
        obj: JSON object (dict, list, or primitive)
        
    Returns:
        Extracted text
    """
    if isinstance(obj, dict):
        texts = []
        for key, value in obj.items():
            # Include key names in the text
            texts.append(str(key))
            texts.append(_extract_text_from_json_object(value))
        return " ".join(texts)
    
    elif isinstance(obj, list):
        texts = []
        for item in obj:
            texts.append(_extract_text_from_json_object(item))
        return " ".join(texts)
    
    elif isinstance(obj, str):
        return obj
    
    elif obj is not None:
        return str(obj)
    
    return ""

def calculate_readability_score(text: str) -> Dict[str, Any]:
    """
    Calculate basic readability metrics
    
    Args:
        text: Input text
        
    Returns:
        Dictionary with readability metrics
    """
    if not text:
        return {"error": "Empty text"}
    
    # Basic statistics
    sentences = text.count('.') + text.count('!') + text.count('?')
    if sentences == 0:
        sentences = 1  # Avoid division by zero
    
    words = len(text.split())
    if words == 0:
        return {"error": "No words found"}
    
    syllables = sum(_count_syllables(word) for word in text.split())
    
    # Flesch Reading Ease Score approximation
    avg_sentence_length = words / sentences
    avg_syllables_per_word = syllables / words
    
    flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
    
    # Flesch-Kincaid Grade Level approximation
    grade_level = (0.39 * avg_sentence_length) + (11.8 * avg_syllables_per_word) - 15.59
    
    # Interpret Flesch score
    if flesch_score >= 90:
        reading_level = "Very Easy"
    elif flesch_score >= 80:
        reading_level = "Easy"
    elif flesch_score >= 70:
        reading_level = "Fairly Easy"
    elif flesch_score >= 60:
        reading_level = "Standard"
    elif flesch_score >= 50:
        reading_level = "Fairly Difficult"
    elif flesch_score >= 30:
        reading_level = "Difficult"
    else:
        reading_level = "Very Difficult"
    
    return {
        "flesch_reading_ease": round(flesch_score, 2),
        "flesch_kincaid_grade": round(grade_level, 2),
        "reading_level": reading_level,
        "avg_sentence_length": round(avg_sentence_length, 2),
        "avg_syllables_per_word": round(avg_syllables_per_word, 2),
        "total_sentences": sentences,
        "total_words": words,
        "total_syllables": syllables
    }

def _count_syllables(word: str) -> int:
    """
    Count syllables in a word (approximation)
    
    Args:
        word: Input word
        
    Returns:
        Number of syllables
    """
    word = word.lower()
    vowels = "aeiouy"
    syllable_count = 0
    prev_was_vowel = False
    
    for char in word:
        if char in vowels:
            if not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = True
        else:
            prev_was_vowel = False
    
    # Handle silent 'e'
    if word.endswith('e') and syllable_count > 1:
        syllable_count -= 1
    
    return max(1, syllable_count)  # Every word has at least one syllable

def get_file_type_category(file_type: str) -> str:
    """
    Categorize file type into broad categories
    
    Args:
        file_type: MIME type
        
    Returns:
        File category (text, image, audio, video, document, archive, other)
    """
    file_type = file_type.lower()
    
    if file_type.startswith('text/'):
        return "text"
    elif file_type.startswith('image/'):
        return "image"
    elif file_type.startswith('audio/'):
        return "audio"
    elif file_type.startswith('video/'):
        return "video"
    elif file_type in ['application/pdf', 'application/msword', 
                      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                      'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                      'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation']:
        return "document"
    elif file_type in ['application/zip', 'application/x-rar-compressed', 'application/x-tar', 'application/gzip']:
        return "archive"
    else:
        return "other"

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted file size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def create_analysis_summary(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a summary of analysis results
    
    Args:
        analysis_results: Dictionary containing analysis results
        
    Returns:
        Summary dictionary
    """
    summary = {
        "analysis_timestamp": datetime.now().isoformat(),
        "analysis_types": list(analysis_results.keys()),
        "success_count": 0,
        "error_count": 0,
        "errors": []
    }
    
    for analysis_type, result in analysis_results.items():
        if isinstance(result, dict) and "error" in result:
            summary["error_count"] += 1
            summary["errors"].append({
                "type": analysis_type,
                "error": result["error"]
            })
        else:
            summary["success_count"] += 1
    
    summary["success_rate"] = (summary["success_count"] / len(analysis_results)) * 100 if analysis_results else 0
    
    return summary 