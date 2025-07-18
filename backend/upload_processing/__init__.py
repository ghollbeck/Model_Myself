"""
Upload Processing Package

This package contains modules for analyzing uploaded documents.
It provides various document analysis capabilities including:
- Text extraction
- Sentiment analysis
- Keyword extraction
- Document summarization
- Metadata extraction

The package is structured to be extensible and support multiple analysis types.
"""

from .processors import (
    TextExtractor,
    SentimentAnalyzer,
    KeywordExtractor,
    DocumentSummarizer,
    MetadataExtractor
)

from .utils import (
    get_file_content,
    detect_language,
    clean_text,
    validate_document_format
)

__version__ = "1.0.0"
__all__ = [
    "TextExtractor",
    "SentimentAnalyzer", 
    "KeywordExtractor",
    "DocumentSummarizer",
    "MetadataExtractor",
    "KnowledgeGraphExtractor",
    "get_file_content",
    "detect_language",
    "clean_text",
    "validate_document_format"
] 