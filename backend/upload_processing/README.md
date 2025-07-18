# Upload Processing System

The Upload Processing System is a comprehensive document analysis framework designed to analyze uploaded documents in the Model Myself application. It provides various analysis capabilities including text extraction, sentiment analysis, keyword extraction, document summarization, and metadata extraction.

## Overview

The system is built with a modular architecture that supports multiple analysis types and can be easily extended with new processors. It works with both MongoDB and local storage backends.

## Architecture

### Core Components

1. **Document Analysis Router** (`routes/document_analysis.py`)
   - Main API endpoints for document analysis
   - Handles analysis requests and queue management
   - Provides status tracking and result retrieval

2. **Analysis Processors** (`upload_processing/processors.py`)
   - Modular processors for different analysis types
   - Base processor class for consistent interface
   - Extensible architecture for adding new analysis types

3. **Utility Functions** (`upload_processing/utils.py`)
   - Common utility functions for text processing
   - File content extraction and validation
   - Language detection and readability analysis

4. **Storage Layer**
   - Analysis results stored in JSON files
   - Queue management for processing requests
   - Integration with existing document storage system

## Available Analysis Types

### 1. Text Extraction
- **Purpose**: Extract text content from various document formats
- **Supported Formats**: TXT, MD, HTML, JSON, CSV, XML
- **Features**: 
  - Format-specific text extraction
  - HTML tag removal
  - Character encoding detection
  - Text statistics (word count, line count, etc.)

### 2. Sentiment Analysis
- **Purpose**: Analyze emotional tone of document content
- **Supported Formats**: TXT, MD, HTML, JSON
- **Features**:
  - Sentiment score calculation
  - Positive/negative/neutral classification
  - Confidence scoring
  - Basic keyword-based analysis

### 3. Keyword Extraction
- **Purpose**: Extract important keywords and phrases
- **Supported Formats**: TXT, MD, HTML, JSON, CSV
- **Features**:
  - Frequency-based keyword extraction
  - Stop word filtering
  - Configurable keyword count
  - Confidence scoring

### 4. Document Summarization
- **Purpose**: Generate concise summaries of document content
- **Supported Formats**: TXT, MD, HTML, JSON
- **Features**:
  - Extractive summarization
  - Configurable summary length
  - Compression ratio calculation
  - Sentence-based extraction

### 5. Metadata Extraction
- **Purpose**: Extract document metadata and structural information
- **Supported Formats**: All formats
- **Features**:
  - File information extraction
  - Content statistics
  - Structure analysis (headers, lists, links, code)
  - Processing information

## API Endpoints

### Analysis Management

#### `POST /document-analysis/analyze`
Start analysis for a specific document.

**Request Body:**
```json
{
  "document_id": "string",
  "analysis_types": ["text_extraction", "sentiment", "keywords"],
  "priority": 5
}
```

**Response:**
```json
{
  "message": "Document analysis started",
  "document_id": "string",
  "filename": "string",
  "analysis_types": ["text_extraction", "sentiment"],
  "status": "queued"
}
```

#### `GET /document-analysis/results/{document_id}`
Get analysis results for a specific document.

**Response:**
```json
{
  "document_id": "string",
  "filename": "string",
  "file_type": "string",
  "status": "completed",
  "results": {
    "text_extraction": {...},
    "sentiment": {...}
  },
  "processing_time_seconds": 2.5
}
```

#### `GET /document-analysis/results`
Get all analysis results with optional filtering.

**Query Parameters:**
- `status`: Filter by status (pending, processing, completed, failed)
- `limit`: Number of results to return (default: 20)
- `skip`: Number of results to skip (default: 0)

### System Information

#### `GET /document-analysis/routes`
Get information about all available routes and system status.

#### `GET /document-analysis/supported-types`
Get list of supported analysis types and their capabilities.

#### `GET /document-analysis/status`
Get analysis processing status and statistics.

#### `GET /document-analysis/queue`
Get current analysis queue status.

#### `GET /document-analysis/health`
Health check endpoint for the analysis service.

## Usage Examples

### Starting Document Analysis

```python
import requests

# Start analysis for a document
response = requests.post("http://localhost:8089/document-analysis/analyze", json={
    "document_id": "document123",
    "analysis_types": ["text_extraction", "sentiment", "keywords"],
    "priority": 3
})

print(response.json())
```

### Retrieving Analysis Results

```python
# Get results for a specific document
response = requests.get("http://localhost:8089/document-analysis/results/document123")
results = response.json()

if results["status"] == "completed":
    print("Analysis completed!")
    print(f"Sentiment: {results['results']['sentiment']['sentiment_label']}")
    print(f"Keywords: {results['results']['keywords']['keywords']}")
```

### Checking System Status

```python
# Get system status
response = requests.get("http://localhost:8089/document-analysis/status")
status = response.json()

print(f"Total analyses: {status['total_analyses']}")
print(f"Success rate: {status['success_rate']}%")
print(f"Queue length: {status['queue_length']}")
```

## File Structure

```
upload_processing/
├── __init__.py              # Package initialization
├── README.md               # This documentation
├── processors.py           # Analysis processors
├── utils.py               # Utility functions
├── analysis_results.json  # Analysis results storage
└── analysis_queue.json    # Processing queue storage
```

## Configuration

The system supports configuration through processor initialization:

```python
# Example processor configuration
config = {
    "max_text_length": 50000,
    "max_keywords": 15,
    "min_text_length": 50,
    "max_summary_length": 300
}

processor = TextExtractor(config)
```

## Extending the System

### Adding New Analysis Types

1. Create a new processor class inheriting from `BaseProcessor`
2. Implement the `process` method
3. Define supported formats in `get_supported_formats`
4. Add the processor to the `__init__.py` file
5. Update the route handler to include the new analysis type

### Example: Custom Processor

```python
class CustomAnalyzer(BaseProcessor):
    def __init__(self, config=None):
        super().__init__(config)
    
    async def process(self, content: str, document_info: Dict[str, Any]) -> Dict[str, Any]:
        # Implement custom analysis logic
        return {"custom_result": "analysis_data"}
    
    def get_supported_formats(self) -> List[str]:
        return ["txt", "md", "html"]
```

## Error Handling

The system provides comprehensive error handling:

- **Input Validation**: Checks for valid document IDs and analysis types
- **Format Validation**: Ensures document formats are supported for requested analysis
- **Processing Errors**: Captures and logs analysis failures
- **Queue Management**: Handles processing queue errors gracefully

## Performance Considerations

- **Background Processing**: Analysis runs in background tasks to avoid blocking API calls
- **Queue Management**: Processing queue prevents system overload
- **Result Caching**: Analysis results are cached to avoid reprocessing
- **Memory Management**: Large documents are processed in chunks when possible

## Security

- **Input Sanitization**: All text inputs are sanitized before processing
- **File Validation**: Document formats are validated before analysis
- **Access Control**: Analysis results are tied to document IDs with proper access controls
- **Error Logging**: Detailed error logging for debugging and monitoring

## Future Enhancements

### Planned Features

1. **Advanced NLP**: Integration with transformer models for better analysis
2. **Multi-language Support**: Enhanced language detection and processing
3. **Batch Processing**: Ability to process multiple documents simultaneously
4. **Real-time Updates**: WebSocket support for real-time analysis status
5. **Export Capabilities**: Export analysis results in various formats
6. **Visualization**: Charts and graphs for analysis results
7. **Machine Learning**: Custom ML models for domain-specific analysis

### Integration Opportunities

1. **Knowledge Graph**: Connect analysis results to the knowledge graph
2. **Training System**: Use analysis results to enhance training data
3. **Search Enhancement**: Improve document search using analysis results
4. **Recommendation System**: Suggest related documents based on analysis

## Troubleshooting

### Common Issues

1. **Analysis Fails**: Check document format compatibility
2. **Slow Processing**: Monitor queue length and system resources
3. **Memory Issues**: Reduce text length limits in processor config
4. **Import Errors**: Ensure all dependencies are installed

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

When contributing to the upload processing system:

1. Follow the existing code structure and patterns
2. Add comprehensive tests for new processors
3. Update documentation for new features
4. Ensure backward compatibility
5. Add proper error handling and logging

## Dependencies

- **FastAPI**: Web framework for API endpoints
- **Pydantic**: Data validation and serialization
- **Motor**: Async MongoDB driver (optional)
- **Python Standard Library**: JSON, datetime, pathlib, etc.

## License

This system is part of the Model Myself application and follows the same licensing terms. 