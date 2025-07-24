from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional, Union, Any
import json
import os
from datetime import datetime
import logging
import sys
from pathlib import Path
import asyncio
from upload_processing.processors import KnowledgeGraphExtractor
from upload_processing.utils import get_file_content
try:
    from analysis.graph import KnowledgeGraph
except ImportError:
    KnowledgeGraph = None

# Add the parent directory to the path to import utilities
sys.path.append(str(Path(__file__).parent.parent))

# --- Robust import of backend main module and shared helpers ---
import importlib

# Try to get the already-loaded main module first to avoid duplicate imports
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
    COLLECTION_NAME = getattr(main_mod, "COLLECTION_NAME", "documents")
    load_local_metadata = getattr(main_mod, "load_local_metadata", None)
    UPLOAD_DIR = getattr(main_mod, "UPLOAD_DIR", Path(__file__).resolve().parent.parent / "uploads")
    METADATA_FILE = getattr(main_mod, "METADATA_FILE", UPLOAD_DIR / "metadata.json")
    # fallback loader that reads the local metadata file directly
    def load_local_metadata():
        try:
            with open(METADATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
else:
    # Fallback if main module cannot be imported
    mongodb_connected = False
    database = None
    COLLECTION_NAME = "documents"
    # Ensure we reference the correct uploads directory relative to the backend package
    UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
    METADATA_FILE = UPLOAD_DIR / "metadata.json"
    # fallback loader that reads the local metadata file directly
    def load_local_metadata():
        try:
            with open(METADATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
# --- end robust import block ---

logger = logging.getLogger(__name__)

router = APIRouter()

# Analysis data file path
ANALYSIS_DATA_FILE = "upload_processing/analysis_results.json"
ANALYSIS_QUEUE_FILE = "upload_processing/analysis_queue.json"

# Ensure upload_processing directory exists
UPLOAD_PROCESSING_DIR = Path("upload_processing")
UPLOAD_PROCESSING_DIR.mkdir(exist_ok=True)

class DocumentAnalysisResult(BaseModel):
    document_id: str
    filename: str
    file_type: str
    file_size: int
    analysis_type: str
    status: str  # "pending", "processing", "completed", "failed"
    results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time_seconds: Optional[float] = None

class AnalysisRequest(BaseModel):
    document_id: str
    analysis_types: List[str]  # ["text_extraction", "sentiment", "keywords", "summary", "metadata"]
    priority: Optional[int] = 5  # 1-10, lower numbers = higher priority

class AnalysisQueueItem(BaseModel):
    document_id: str
    filename: str
    file_type: str
    analysis_types: List[str]
    priority: int
    created_at: datetime
    status: str  # "queued", "processing", "completed", "failed"

def load_analysis_data():
    """Load analysis results from file"""
    try:
        if Path(ANALYSIS_DATA_FILE).exists():
            with open(ANALYSIS_DATA_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"Error loading analysis data: {e}")
        return []

def save_analysis_data(data):
    """Save analysis results to file"""
    try:
        with open(ANALYSIS_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    except Exception as e:
        logger.error(f"Error saving analysis data: {e}")

def load_analysis_queue():
    """Load analysis queue from file"""
    try:
        if Path(ANALYSIS_QUEUE_FILE).exists():
            with open(ANALYSIS_QUEUE_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"Error loading analysis queue: {e}")
        return []

def save_analysis_queue(queue):
    """Save analysis queue to file"""
    try:
        with open(ANALYSIS_QUEUE_FILE, 'w') as f:
            json.dump(queue, f, indent=2, default=str)
    except Exception as e:
        logger.error(f"Error saving analysis queue: {e}")

async def get_document_info(document_id: str):
    """Get document information from MongoDB or local storage"""
    logger.debug(f"get_document_info() called with id={document_id}")
    try:
        # Get current MongoDB connection status from main module
        main_mod = sys.modules.get("main")
        current_mongodb_connected = False
        current_database = None
        
        if main_mod:
            current_mongodb_connected = getattr(main_mod, "mongodb_connected", False)
            current_database = getattr(main_mod, "database", None)
        
        logger.debug(f"Current MongoDB connection status: {current_mongodb_connected}")
        
        if current_mongodb_connected and current_database is not None:
            from bson import ObjectId
            try:
                document = await current_database[COLLECTION_NAME].find_one({"_id": ObjectId(document_id)})
                logger.debug(f"MongoDB query result: {document is not None}")
                if document:
                    return {
                        "id": str(document["_id"]),
                        "filename": document["filename"],
                        "file_type": document["file_type"],
                        "file_size": document["file_size"],
                        "content_type": document["content_type"],
                        "upload_date": document["upload_date"],
                        "category": document.get("category", ""),
                        "file_id": document.get("file_id"),  # Include file_id for GridFS retrieval
                        "local_path": None
                    }
            except Exception as e:
                logger.error(f"MongoDB query failed: {e}")
                # Fall through to local storage
        
        # Local storage fallback
        if callable(load_local_metadata):
            metadata = load_local_metadata()
        else:
            # Direct file loading if import failed
            try:
                with open(METADATA_FILE, 'r') as f:
                    metadata = json.load(f)
            except:
                metadata = []

        logger.debug(f"Loaded local metadata entries: {len(metadata)}")
        if metadata:
            sample_ids = [m.get('id') for m in metadata[:10]]
            logger.debug(f"First 10 document IDs in metadata: {sample_ids}")

        document = next((doc for doc in metadata if doc["id"] == document_id), None)
        if not document:
            logger.warning(f"Document id {document_id} not found in local metadata. Total entries: {len(metadata)}")
        if document:
            return {
                "id": document["id"],
                "filename": document["filename"],
                "file_type": document["file_type"],
                "file_size": document["file_size"],
                "content_type": document["content_type"],
                "upload_date": document["upload_date"],
                "category": document.get("category", ""),
                "local_path": document.get("local_path")
            }
    except Exception as e:
        logger.error(f"Error getting document info for {document_id}: {e}")
    return None

async def analyze_document_placeholder(document_info: dict, analysis_types: List[str]) -> Dict[str, Any]:
    """
    Updated analysis function that supports knowledge_extraction via LLM
    """
    logger.info(f"Analyzing document: {document_info['filename']} with types: {analysis_types}")

    results = {}

    # Load file content when needed
    content: Optional[str] = None
    if any(at in analysis_types for at in ["knowledge_extraction"]):
        content = await get_file_content(document_info)
        if content is None:
            logger.error("Failed to retrieve file content for knowledge extraction")

    for analysis_type in analysis_types:
        if analysis_type == "knowledge_extraction":
            kg_extractor = KnowledgeGraphExtractor()
            res = await kg_extractor.process(content or "", document_info)
            results[analysis_type] = res
        elif analysis_type == "text_extraction":
            results["text_extraction"] = {
                "extracted_text": content or "",
                "text_length": len(content or ""),
                "language": "en"
            }
        # keep existing simple placeholders for other types
        elif analysis_type == "sentiment":
            results["sentiment"] = {
                "score": 0.0,
                "label": "neutral",
                "confidence": 0.5
            }
        elif analysis_type == "keywords":
            results["keywords"] = {
                "keywords": [],
                "confidence_scores": []
            }
        elif analysis_type == "summary":
            results["summary"] = {
                "summary": "",
                "summary_length": 0,
                "compression_ratio": 0.0
            }
        elif analysis_type == "metadata":
            results["metadata"] = {
                "word_count": len((content or "").split()),
                "character_count": len(content or "")
            }

    # If knowledge entries extracted, store them into KnowledgeGraph under a new blue document node
    kg_res = results.get("knowledge_extraction")
    if kg_res and isinstance(kg_res, dict) and kg_res.get("error"):
        logger.warning(f"Knowledge extraction returned error: {kg_res['error']}")
    if kg_res and isinstance(kg_res, dict) and kg_res.get("entries") and KnowledgeGraph:
        try:
            logger.info(f"Processing {len(kg_res['entries'])} knowledge graph entries from document analysis")
            kg = KnowledgeGraph()
            # Load existing graph if present
            try:
                kg.load("knowledge_graph.pkl")
                logger.info(f"Loaded existing knowledge graph with {len(kg.graph.nodes)} nodes and {len(kg.graph.edges)} edges")
            except Exception as e:
                logger.info(f"No existing knowledge graph found, creating new one: {e}")

            # Ensure main Documents hub exists
            if "Documents" not in kg.graph:
                kg.graph.add_node("Documents", type="document_main", color="blue")
                logger.info("🔵 Created main 'Documents' hub node - marked BLUE (type=document_main)")
            else:
                logger.info("🔵 Main 'Documents' hub node already exists - ensuring BLUE color")
                kg.graph.nodes["Documents"]["color"] = "blue"  # Ensure it stays blue

            # Create (or fetch existing) node for this specific document
            doc_node_id = f"Doc_{document_info['id']}"
            if doc_node_id not in kg.graph:
                kg.graph.add_node(
                    doc_node_id,
                    type="document_instance",  # This ensures blue color in frontend visualization
                    filename=document_info.get("filename", ""),
                    document_id=document_info["id"],
                    file_type=document_info.get("file_type", ""),
                    file_size=document_info.get("file_size", 0),
                    upload_date=str(document_info.get("upload_date", "")),
                    analysis_timestamp=datetime.now().isoformat(),
                    color="blue"  # Explicit blue color marking for knowledge graph visualization
                )
                kg.graph.add_edge("Documents", doc_node_id)
                logger.info(f"🔵 Created BLUE document node: {doc_node_id} for file '{document_info.get('filename', '')}' (type=document_instance)")
            else:
                # Update existing node with latest analysis timestamp
                kg.graph.nodes[doc_node_id]["analysis_timestamp"] = datetime.now().isoformat()
                logger.info(f"🔵 Updated existing BLUE document node: {doc_node_id} with new analysis timestamp")

            # Add each extracted entry and connect to this document node
            added_entries = 0
            for i, entry in enumerate(kg_res["entries"]):
                category = entry.get("category", "Knowledge")
                question = entry.get("question", "Unknown question")
                answer = entry.get("answer", "")

                logger.debug(f"Processing entry {i+1}: Category='{category}', Question='{question[:50]}...', Answer='{answer[:50]}...'")

                # Use fallback category if unknown
                try:
                    node_id = kg.add_entry(category, question, answer)
                    logger.debug(f"Added knowledge entry with node ID: {node_id}")
                except ValueError as e:
                    logger.warning(f"Category '{category}' not valid, using 'Knowledge' fallback: {e}")
                    node_id = kg.add_entry("Knowledge", question, answer)

                kg.add_relationship(doc_node_id, node_id, "contains")
                logger.debug(f"Added relationship: {doc_node_id} -> {node_id} (contains)")
                added_entries += 1

            logger.info(f"Successfully processed {added_entries} knowledge graph entries")
            
            # Save the updated graph
            kg.save("knowledge_graph.pkl")
            logger.info(f"Saved updated knowledge graph with {len(kg.graph.nodes)} nodes and {len(kg.graph.edges)} edges to knowledge_graph.pkl")
            
            logger.info(
                f"Knowledge graph integration complete: {added_entries} entries from document '{document_info.get('filename', '')}' stored under node {doc_node_id}"
            )
        except Exception as e:
            logger.error(f"Failed to store entries in knowledge graph: {e}")
            import traceback
            logger.error(f"Knowledge graph error traceback: {traceback.format_exc()}")

    return results

async def process_document_analysis(document_id: str, analysis_types: List[str]):
    """Background task to process document analysis"""
    logger.info(f"Starting analysis for document {document_id}")
    
    # Get document info
    document_info = await get_document_info(document_id)
    if not document_info:
        logger.error(f"Document {document_id} not found")
        return
    
    # Load analysis data
    analysis_data = load_analysis_data()
    
    # Create or update analysis record
    analysis_record = None
    for record in analysis_data:
        if record["document_id"] == document_id:
            analysis_record = record
            break
    
    if not analysis_record:
        analysis_record = {
            "document_id": document_id,
            "filename": document_info["filename"],
            "file_type": document_info["file_type"],
            "file_size": document_info["file_size"],
            "analysis_type": ", ".join(analysis_types),
            "status": "processing",
            "results": None,
            "error_message": None,
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "processing_time_seconds": None
        }
        analysis_data.append(analysis_record)
    else:
        analysis_record["status"] = "processing"
        analysis_record["started_at"] = datetime.now().isoformat()
        analysis_record["error_message"] = None
    
    # Save initial state
    save_analysis_data(analysis_data)
    
    try:
        # Perform analysis
        start_time = datetime.now()
        results = await analyze_document_placeholder(document_info, analysis_types)
        end_time = datetime.now()
        
        # Update record with results
        analysis_record["status"] = "completed"
        analysis_record["results"] = results
        analysis_record["completed_at"] = end_time.isoformat()
        analysis_record["processing_time_seconds"] = (end_time - start_time).total_seconds()
        
        logger.info(f"Analysis completed for document {document_id}")
        
    except Exception as e:
        # Update record with error
        analysis_record["status"] = "failed"
        analysis_record["error_message"] = str(e)
        analysis_record["completed_at"] = datetime.now().isoformat()
        
        logger.error(f"Analysis failed for document {document_id}: {e}")
    
    # Save final state
    save_analysis_data(analysis_data)

@router.get("/routes")
async def get_available_routes():
    """Get information about all available document analysis routes"""
    # Get current MongoDB connection status from main module
    main_mod = sys.modules.get("main")
    current_mongodb_connected = False
    
    if main_mod:
        current_mongodb_connected = getattr(main_mod, "mongodb_connected", False)
    
    routes_info = {
        "analysis_routes": [
            {
                "path": "/analyze",
                "method": "POST",
                "description": "Start analysis for a specific document",
                "parameters": ["document_id", "analysis_types"]
            },
            {
                "path": "/results/{document_id}",
                "method": "GET",
                "description": "Get analysis results for a specific document"
            },
            {
                "path": "/results",
                "method": "GET", 
                "description": "Get all analysis results with optional filtering"
            },
            {
                "path": "/status",
                "method": "GET",
                "description": "Get analysis processing status and statistics"
            },
            {
                "path": "/queue",
                "method": "GET",
                "description": "Get current analysis queue"
            },
            {
                "path": "/supported-types",
                "method": "GET",
                "description": "Get supported analysis types"
            }
        ],
        "upload_system_info": {
            "storage_mode": "MongoDB" if current_mongodb_connected else "Local Storage",
            "upload_endpoint": "/upload",
            "documents_endpoint": "/documents",
            "supported_formats": ["txt", "pdf", "doc", "docx", "json", "csv", "md", "html", "xml"]
        }
    }
    return routes_info

@router.get("/supported-types")
async def get_supported_analysis_types():
    """Get list of supported analysis types"""
    return {
        "supported_types": [
            {
                "type": "knowledge_extraction",
                "description": "Extract structured entries for the knowledge graph using LLM",
                "supported_formats": ["text/plain", "text/markdown"]
            },
            {
                "type": "text_extraction",
                "description": "Extract text content from documents",
                "supported_formats": ["pdf", "doc", "docx", "txt", "html", "md"]
            },
            {
                "type": "sentiment",
                "description": "Analyze sentiment of document content",
                "supported_formats": ["txt", "md", "html", "json"]
            },
            {
                "type": "keywords",
                "description": "Extract keywords and key phrases",
                "supported_formats": ["txt", "md", "html", "json", "pdf"]
            },
            {
                "type": "summary",
                "description": "Generate document summary",
                "supported_formats": ["txt", "md", "html", "json", "pdf"]
            },
            {
                "type": "metadata",
                "description": "Extract document metadata and statistics",
                "supported_formats": ["all"]
            }
        ]
    }

@router.post("/analyze")
async def analyze_document(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Start analysis for a specific document"""
    logger.info(f"Analysis request received for document {request.document_id}")

    # Extra debug details about incoming request
    logger.debug(f"Request body: analysis_types={request.analysis_types}, priority={request.priority}")
    
    # Check if document exists
    document_info = await get_document_info(request.document_id)
    logger.debug(f"get_document_info returned: {document_info is not None}")
    if not document_info:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Add to processing queue
    background_tasks.add_task(process_document_analysis, request.document_id, request.analysis_types)
    
    return {
        "message": "Document analysis started",
        "document_id": request.document_id,
        "filename": document_info["filename"],
        "analysis_types": request.analysis_types,
        "status": "queued"
    }

@router.get("/results/{document_id}")
async def get_analysis_results(document_id: str):
    """Get analysis results for a specific document"""
    logger.info(f"Getting analysis results for document {document_id}")
    
    analysis_data = load_analysis_data()
    
    # Find analysis record
    analysis_record = None
    for record in analysis_data:
        if record["document_id"] == document_id:
            analysis_record = record
            break
    
    if not analysis_record:
        raise HTTPException(status_code=404, detail="No analysis found for this document")
    
    return analysis_record

@router.get("/results")
async def get_all_analysis_results(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(20, description="Number of results to return"),
    skip: int = Query(0, description="Number of results to skip")
):
    """Get all analysis results with optional filtering"""
    logger.info(f"Getting analysis results with filters: status={status}, limit={limit}, skip={skip}")
    
    analysis_data = load_analysis_data()
    
    # Apply status filter
    if status:
        analysis_data = [record for record in analysis_data if record["status"] == status]
    
    # Sort by completion date (newest first)
    analysis_data.sort(key=lambda x: x.get("completed_at", x.get("started_at", "")), reverse=True)
    
    # Apply pagination
    total_count = len(analysis_data)
    paginated_data = analysis_data[skip:skip + limit]
    
    return {
        "results": paginated_data,
        "total_count": total_count,
        "has_more": (skip + len(paginated_data)) < total_count
    }

@router.get("/status")
async def get_analysis_status():
    """Get analysis processing status and statistics"""
    logger.info("Getting analysis status")
    
    analysis_data = load_analysis_data()
    
    # Calculate statistics
    total_analyses = len(analysis_data)
    status_counts = {}
    
    for record in analysis_data:
        status = record["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Calculate average processing time
    completed_analyses = [r for r in analysis_data if r["status"] == "completed" and r.get("processing_time_seconds")]
    avg_processing_time = sum(r["processing_time_seconds"] for r in completed_analyses) / len(completed_analyses) if completed_analyses else 0
    
    return {
        "total_analyses": total_analyses,
        "status_counts": status_counts,
        "average_processing_time_seconds": avg_processing_time,
        "queue_length": status_counts.get("queued", 0) + status_counts.get("processing", 0),
        "success_rate": (status_counts.get("completed", 0) / total_analyses * 100) if total_analyses > 0 else 0
    }

@router.get("/queue")
async def get_analysis_queue():
    """Get current analysis queue"""
    logger.info("Getting analysis queue")
    
    analysis_data = load_analysis_data()
    
    # Get queued and processing items
    queue_items = [record for record in analysis_data if record["status"] in ["queued", "processing"]]
    
    # Sort by priority and creation time
    queue_items.sort(key=lambda x: (x.get("priority", 5), x.get("started_at", "")))
    
    return {
        "queue": queue_items,
        "queue_length": len(queue_items)
    }

@router.delete("/results/{document_id}")
async def delete_analysis_results(document_id: str):
    """Delete analysis results for a specific document"""
    logger.info(f"Deleting analysis results for document {document_id}")
    
    analysis_data = load_analysis_data()
    
    # Find and remove analysis record
    original_count = len(analysis_data)
    analysis_data = [record for record in analysis_data if record["document_id"] != document_id]
    
    if len(analysis_data) == original_count:
        raise HTTPException(status_code=404, detail="No analysis found for this document")
    
    save_analysis_data(analysis_data)
    
    return {"message": "Analysis results deleted successfully"}

@router.get("/health")
async def health_check():
    """Health check for document analysis service"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "upload_processing_dir": str(UPLOAD_PROCESSING_DIR),
        "analysis_data_file": ANALYSIS_DATA_FILE,
        "queue_file": ANALYSIS_QUEUE_FILE
    } 