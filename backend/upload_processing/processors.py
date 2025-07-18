"""
Document Analysis Processors

This module contains different processors for analyzing uploaded documents.
Each processor is designed to handle specific types of analysis.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import re
import json
from pathlib import Path
import os
import anthropic
import json as _json
from asyncio import get_event_loop

logger = logging.getLogger(__name__)

class BaseProcessor(ABC):
    """Base class for all document processors"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.name = self.__class__.__name__
        
    @abstractmethod
    async def process(self, content: str, document_info: Dict[str, Any]) -> Dict[str, Any]:
        """Process document content and return analysis results"""
        pass
    
    def validate_input(self, content: str, document_info: Dict[str, Any]) -> bool:
        """Validate input before processing"""
        if not content or not isinstance(content, str):
            return False
        if not document_info or not isinstance(document_info, dict):
            return False
        return True
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats"""
        return ["txt", "md", "html", "json"]

class TextExtractor(BaseProcessor):
    """Extract text content from various document formats"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.max_text_length = self.config.get("max_text_length", 100000)
    
    async def process(self, content: str, document_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract text from document content"""
        if not self.validate_input(content, document_info):
            return {"error": "Invalid input"}
        
        try:
            file_type = document_info.get("file_type", "").lower()
            extracted_text = ""
            
            if file_type in ["text/plain", "text/markdown", "application/json"]:
                extracted_text = content
            elif file_type in ["text/html", "application/html"]:
                # Basic HTML tag removal
                extracted_text = re.sub(r'<[^>]+>', '', content)
            else:
                # For other formats, return as-is for now
                extracted_text = content
            
            # Truncate if too long
            if len(extracted_text) > self.max_text_length:
                extracted_text = extracted_text[:self.max_text_length] + "..."
            
            # Basic text statistics
            word_count = len(extracted_text.split())
            char_count = len(extracted_text)
            line_count = extracted_text.count('\n') + 1
            
            return {
                "extracted_text": extracted_text,
                "text_length": len(extracted_text),
                "word_count": word_count,
                "character_count": char_count,
                "line_count": line_count,
                "language": self._detect_language(extracted_text),
                "extraction_method": "basic_text_extraction"
            }
            
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return {"error": f"Text extraction failed: {str(e)}"}
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection (placeholder)"""
        # This is a placeholder - in a real implementation you'd use a library like langdetect
        if len(text) < 10:
            return "unknown"
        return "en"  # Default to English
    
    def get_supported_formats(self) -> List[str]:
        return ["txt", "md", "html", "json", "csv", "xml"]

class SentimentAnalyzer(BaseProcessor):
    """Analyze sentiment of document content"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.min_text_length = self.config.get("min_text_length", 10)
    
    async def process(self, content: str, document_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment of document content"""
        if not self.validate_input(content, document_info):
            return {"error": "Invalid input"}
        
        try:
            # Clean the text
            clean_text = self._clean_text(content)
            
            if len(clean_text) < self.min_text_length:
                return {"error": "Text too short for sentiment analysis"}
            
            # Placeholder sentiment analysis
            # In a real implementation, you'd use a library like VADER, TextBlob, or a ML model
            sentiment_score = self._analyze_sentiment_placeholder(clean_text)
            
            return {
                "sentiment_score": sentiment_score,
                "sentiment_label": self._score_to_label(sentiment_score),
                "confidence": 0.85,  # Placeholder confidence
                "text_length": len(clean_text),
                "analysis_method": "placeholder_sentiment"
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {"error": f"Sentiment analysis failed: {str(e)}"}
    
    def _clean_text(self, text: str) -> str:
        """Clean text for sentiment analysis"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        return text
    
    def _analyze_sentiment_placeholder(self, text: str) -> float:
        """Placeholder sentiment analysis"""
        # Very basic sentiment analysis based on keywords
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic"]
        negative_words = ["bad", "terrible", "awful", "horrible", "disgusting", "hate"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count + negative_count == 0:
            return 0.0  # Neutral
        
        return (positive_count - negative_count) / (positive_count + negative_count)
    
    def _score_to_label(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score > 0.1:
            return "positive"
        elif score < -0.1:
            return "negative"
        else:
            return "neutral"
    
    def get_supported_formats(self) -> List[str]:
        return ["txt", "md", "html", "json"]

class KeywordExtractor(BaseProcessor):
    """Extract keywords and key phrases from document content"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.max_keywords = self.config.get("max_keywords", 10)
        self.min_word_length = self.config.get("min_word_length", 3)
    
    async def process(self, content: str, document_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract keywords from document content"""
        if not self.validate_input(content, document_info):
            return {"error": "Invalid input"}
        
        try:
            # Clean and tokenize text
            clean_text = self._clean_text(content)
            keywords = self._extract_keywords_placeholder(clean_text)
            
            return {
                "keywords": keywords[:self.max_keywords],
                "keyword_count": len(keywords),
                "extraction_method": "frequency_based",
                "confidence_scores": [0.9 - (i * 0.1) for i in range(len(keywords[:self.max_keywords]))],
                "text_length": len(clean_text)
            }
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return {"error": f"Keyword extraction failed: {str(e)}"}
    
    def _clean_text(self, text: str) -> str:
        """Clean text for keyword extraction"""
        # Remove punctuation and normalize
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text.strip())
        return text.lower()
    
    def _extract_keywords_placeholder(self, text: str) -> List[str]:
        """Placeholder keyword extraction"""
        # Simple frequency-based extraction
        words = text.split()
        
        # Filter out stop words (basic list)
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "will", "would", "could", "should", "may", "might", "must", "can", "this", "that", "these", "those", "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them"}
        
        # Count word frequencies
        word_freq = {}
        for word in words:
            if len(word) >= self.min_word_length and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        keywords = sorted(word_freq.keys(), key=lambda x: word_freq[x], reverse=True)
        return keywords
    
    def get_supported_formats(self) -> List[str]:
        return ["txt", "md", "html", "json", "csv"]

class DocumentSummarizer(BaseProcessor):
    """Generate summaries of document content"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.max_summary_length = self.config.get("max_summary_length", 500)
        self.min_text_length = self.config.get("min_text_length", 100)
    
    async def process(self, content: str, document_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of document content"""
        if not self.validate_input(content, document_info):
            return {"error": "Invalid input"}
        
        try:
            clean_text = self._clean_text(content)
            
            if len(clean_text) < self.min_text_length:
                return {"error": "Text too short for summarization"}
            
            summary = self._generate_summary_placeholder(clean_text)
            
            return {
                "summary": summary,
                "summary_length": len(summary),
                "original_length": len(clean_text),
                "compression_ratio": len(summary) / len(clean_text),
                "summarization_method": "extractive_placeholder"
            }
            
        except Exception as e:
            logger.error(f"Document summarization failed: {e}")
            return {"error": f"Document summarization failed: {str(e)}"}
    
    def _clean_text(self, text: str) -> str:
        """Clean text for summarization"""
        # Basic cleaning
        text = re.sub(r'\s+', ' ', text.strip())
        return text
    
    def _generate_summary_placeholder(self, text: str) -> str:
        """Placeholder summarization"""
        # Simple extractive summarization - take first few sentences
        sentences = text.split('. ')
        
        if len(sentences) <= 3:
            return text
        
        # Take first 3 sentences or until max length
        summary = ""
        for sentence in sentences[:3]:
            if len(summary + sentence) > self.max_summary_length:
                break
            summary += sentence + ". "
        
        return summary.strip()
    
    def get_supported_formats(self) -> List[str]:
        return ["txt", "md", "html", "json"]

class MetadataExtractor(BaseProcessor):
    """Extract metadata and statistics from documents"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
    
    async def process(self, content: str, document_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from document"""
        if not self.validate_input(content, document_info):
            return {"error": "Invalid input"}
        
        try:
            metadata = {
                "file_info": {
                    "filename": document_info.get("filename", ""),
                    "file_type": document_info.get("file_type", ""),
                    "file_size": document_info.get("file_size", 0),
                    "upload_date": document_info.get("upload_date", ""),
                    "category": document_info.get("category", "")
                },
                "content_stats": {
                    "character_count": len(content),
                    "word_count": len(content.split()),
                    "line_count": content.count('\n') + 1,
                    "paragraph_count": len([p for p in content.split('\n\n') if p.strip()]),
                    "average_word_length": self._calculate_avg_word_length(content),
                    "language": self._detect_language(content)
                },
                "structure_analysis": {
                    "has_headers": self._has_headers(content),
                    "has_lists": self._has_lists(content),
                    "has_links": self._has_links(content),
                    "has_code": self._has_code(content)
                },
                "processing_info": {
                    "extraction_timestamp": datetime.now().isoformat(),
                    "processor_version": "1.0.0"
                }
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            return {"error": f"Metadata extraction failed: {str(e)}"}
    
    def _calculate_avg_word_length(self, text: str) -> float:
        """Calculate average word length"""
        words = text.split()
        if not words:
            return 0.0
        return sum(len(word) for word in words) / len(words)
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection"""
        # Placeholder - would use proper language detection library
        return "en"
    
    def _has_headers(self, text: str) -> bool:
        """Check if text has header-like structures"""
        # Look for markdown headers or line patterns
        return bool(re.search(r'^#{1,6}\s', text, re.MULTILINE))
    
    def _has_lists(self, text: str) -> bool:
        """Check if text has list structures"""
        # Look for bullet points or numbered lists
        return bool(re.search(r'^\s*[-*+]\s', text, re.MULTILINE) or 
                   re.search(r'^\s*\d+\.\s', text, re.MULTILINE))
    
    def _has_links(self, text: str) -> bool:
        """Check if text has links"""
        # Look for URLs or markdown links
        return bool(re.search(r'https?://\S+', text) or 
                   re.search(r'\[.*\]\(.*\)', text))
    
    def _has_code(self, text: str) -> bool:
        """Check if text has code blocks"""
        # Look for code blocks or inline code
        return bool(re.search(r'```.*```', text, re.DOTALL) or 
                   re.search(r'`[^`]+`', text))
    
    def get_supported_formats(self) -> List[str]:
        return ["all"]  # Metadata can be extracted from any format 

class KnowledgeGraphExtractor(BaseProcessor):
    """Extract knowledge graph entries (category, question, answer) from text using an LLM"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        # Maximum tokens in prompt to avoid overrun
        self.max_prompt_chars = self.config.get("max_prompt_chars", 8000)
        # OpenAI model name (can be overridden via env var or config)
        self.model_name = self.config.get("model", os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"))

    async def process(self, content: str, document_info: Dict[str, Any]) -> Dict[str, Any]:
        """Call LLM to extract knowledge graph entries from content"""
        if not self.validate_input(content, document_info):
            return {"error": "Invalid input"}

        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                return {"error": "ANTHROPIC_API_KEY environment variable is not set"}

            client = anthropic.Anthropic(api_key=api_key)

            # Truncate content if too long for prompt
            if len(content) > self.max_prompt_chars:
                content = content[: self.max_prompt_chars] + "..."

            system_prompt = (
                "You are an assistant that extracts structured knowledge graph entries "
                "from raw user text. For any facts you can identify that relate to the user's "
                "personality, memories, preferences, morals, feelings, or general knowledge, "
                "output a JSON array where each element has: category, question, answer. "
                "Return ONLY valid JSON. Use existing categories if clear, otherwise pick the closest."
            )
            user_prompt = f"""Extract knowledge graph entries from the following text:\n\n""" + content

            # Because openai's async API requires aiohttp which may not be installed, run sync call in executor
            loop = get_event_loop()

            def _call_anthropic():
                try:
                    # Use messages (Claude 3)
                    resp = client.messages.create(
                        model=self.model_name,
                        max_tokens=512,
                        temperature=0.2,
                        system=system_prompt,
                        messages=[{"role": "user", "content": user_prompt}]
                    )
                    # Combine text blocks
                    text_blocks = []
                    for block in resp.content:
                        if hasattr(block, "text"):
                            text_blocks.append(block.text)
                    return "".join(text_blocks)
                except Exception:
                    # Fallback to completion API if messages not supported
                    prompt = f"{anthropic.HUMAN_PROMPT} {system_prompt}\n{user_prompt}{anthropic.AI_PROMPT}"
                    resp = client.completions.create(
                        model="claude-v1",
                        max_tokens_to_sample=512,
                        temperature=0.2,
                        prompt=prompt
                    )
                    return resp.completion

            content_str = await loop.run_in_executor(None, _call_anthropic)

            # ---------------- Robust JSON parsing ----------------
            raw_output = content_str.strip()
            if raw_output.startswith("```"):
                # Remove leading and trailing fences and optional language tag
                # Pattern: ```json\n...\n```
                parts = raw_output.split("```")
                if len(parts) >= 3:
                    raw_output = "```".join(parts[1:-1])  # middle section(s)
                raw_output = raw_output.lstrip().removeprefix("json").lstrip("\n").strip()

            try:
                entries = _json.loads(raw_output)
            except Exception as e:
                logger.error(
                    f"Failed to parse LLM JSON output after cleanup: {e}\nSnippet: {raw_output[:300]}"
                )
                return {"error": "LLM output parse error"}

            logger.info(
                f"KnowledgeGraphExtractor parsed {len(entries) if isinstance(entries, list) else 'unknown'} entries from LLM"
            )

            if not isinstance(entries, list):
                return {"error": "LLM output not a JSON array"}

            # Validate each entry structure
            valid_entries = []
            for entry in entries:
                if (
                    isinstance(entry, dict)
                    and "category" in entry
                    and "question" in entry
                    and "answer" in entry
                ):
                    valid_entries.append({
                        "category": str(entry["category"].strip()),
                        "question": str(entry["question"].strip()),
                        "answer": str(entry["answer"].strip())
                    })
            if not valid_entries:
                return {"error": "No valid entries extracted"}

            return {
                "entries": valid_entries,
                "entry_count": len(valid_entries),
                "model": self.model_name
            }
        except Exception as e:
            logger.error(f"Knowledge graph extraction failed: {e}")
            return {"error": f"Knowledge graph extraction failed: {str(e)}"}

    def get_supported_formats(self) -> List[str]:
        # Primarily designed for plain text
        return ["text/plain", "text/markdown"] 