from fastapi import FastAPI, HTTPException, UploadFile, File, Query, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import logging
import uvicorn
from datetime import datetime
from typing import List, Optional
import os
import io
import json
import shutil
from pathlib import Path

# MongoDB imports (optional)
try:
    from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
    from bson import ObjectId
    import magic
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

from pydantic import BaseModel

# Import knowledge graph from analysis module
import sys
sys.path.append(str(Path(__file__).parent))
from analysis.graph import KnowledgeGraph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# MongoDB Configuration
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "model_myself"
COLLECTION_NAME = "documents"

# Global variables for MongoDB
mongodb_client = None
database = None
fs_bucket = None
mongodb_connected = False

# Local storage fallback
UPLOAD_DIR = Path("uploads")
METADATA_FILE = UPLOAD_DIR / "metadata.json"

# Pydantic models for API responses
class DocumentMetadata(BaseModel):
    id: str
    filename: str
    content_type: str
    file_size: int
    upload_date: datetime
    file_type: str
    description: Optional[str] = None

class DocumentResponse(BaseModel):
    message: str
    documents: List[DocumentMetadata]

app = FastAPI(
    title="Model Myself Backend with MongoDB",
    description="Backend API for Model Myself application with MongoDB document storage",
    version="2.0.0"
)

# Add CORS middleware to allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def ensure_upload_dir():
    """Ensure upload directory exists"""
    UPLOAD_DIR.mkdir(exist_ok=True)
    if not METADATA_FILE.exists():
        METADATA_FILE.write_text("[]")

def load_local_metadata():
    """Load metadata from local file"""
    try:
        with open(METADATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_local_metadata(metadata):
    """Save metadata to local file"""
    try:
        with open(METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
    except Exception as e:
        logger.error(f"Error saving metadata: {e}")

async def connect_to_mongodb():
    """Connect to MongoDB and initialize GridFS"""
    global mongodb_client, database, fs_bucket, mongodb_connected
    
    if not MONGODB_AVAILABLE:
        logger.warning("MongoDB libraries not available. Using local storage fallback.")
        return False
    
    try:
        mongodb_client = AsyncIOMotorClient(MONGODB_URL)
        database = mongodb_client[DATABASE_NAME]
        fs_bucket = AsyncIOMotorGridFSBucket(database, bucket_name="documents")
        
        # Test the connection
        await mongodb_client.admin.command('ping')
        logger.info(f"Successfully connected to MongoDB at {MONGODB_URL}")
        logger.info(f"Using database: {DATABASE_NAME}")
        mongodb_connected = True
        return True
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        logger.info("Falling back to local storage mode")
        mongodb_connected = False
        return False

async def close_mongodb_connection():
    """Close MongoDB connection"""
    global mongodb_client, mongodb_connected
    if mongodb_client:
        mongodb_client.close()
        logger.info("MongoDB connection closed")
    mongodb_connected = False

@app.on_event("startup")
async def startup_event():
    logger.info("Backend application started")
    logger.info("Hello World from Backend!")
    
    # Try to connect to MongoDB
    await connect_to_mongodb()
    
    # Ensure local storage is ready
    ensure_upload_dir()
    
    if mongodb_connected:
        logger.info("✅ Running in MongoDB mode")
    else:
        logger.info("⚠️  Running in local storage mode")

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongodb_connection()

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    storage_mode = "MongoDB" if mongodb_connected else "Local Storage"
    return {"message": f"Model Myself Backend is running! (Storage: {storage_mode})"}

@app.get("/hello")
async def hello_world():
    logger.info("Hello endpoint accessed")
    
    # Log the request details
    timestamp = datetime.now().isoformat()
    logger.info(f"Processing hello request at {timestamp}")
    
    # The response message as requested
    response_message = "helo1234"
    
    # Log the response
    logger.info(f"Returning response: {response_message}")
    
    return JSONResponse(
        content={"message": response_message},
        status_code=200
    )

@app.get("/health")
async def health_check():
    logger.info("Health check endpoint accessed")
    
    # Check MongoDB connection
    if mongodb_connected:
        try:
            await mongodb_client.admin.command('ping')
            mongodb_status = "connected"
        except Exception as e:
            mongodb_status = f"disconnected: {str(e)}"
    else:
        mongodb_status = "not available - using local storage"
    
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "mongodb_status": mongodb_status,
        "storage_mode": "MongoDB" if mongodb_connected else "Local Storage"
    }

def detect_file_type(file_content: bytes, filename: str) -> str:
    """Detect file type using python-magic or fallback to extension"""
    try:
        if MONGODB_AVAILABLE:
            import magic
            mime_type = magic.from_buffer(file_content, mime=True)
            return mime_type
    except Exception as e:
        logger.warning(f"Could not detect file type for {filename}: {str(e)}")
    
    # Fallback to extension-based detection
    ext = filename.split('.')[-1].lower() if '.' in filename else 'unknown'
    mime_types = {
        'txt': 'text/plain',
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'mp4': 'video/mp4',
        'mp3': 'audio/mpeg',
        'json': 'application/json',
        'csv': 'text/csv',
        'xml': 'application/xml',
        'html': 'text/html',
        'css': 'text/css',
        'js': 'application/javascript',
        'py': 'text/x-python',
        'md': 'text/markdown'
    }
    return mime_types.get(ext, f"application/{ext}")

async def store_file_mongodb(file: UploadFile, file_content: bytes, file_size: int, detected_type: str, category: str = None):
    """Store file in MongoDB"""
    # Create metadata
    metadata = {
        "filename": file.filename,
        "content_type": file.content_type or detected_type,
        "file_size": file_size,
        "upload_date": datetime.now(),
        "file_type": detected_type,
        "original_content_type": file.content_type,
        "category": category
    }
    
    # Store file in GridFS
    file_id = await fs_bucket.upload_from_stream(
        file.filename,
        io.BytesIO(file_content),
        metadata=metadata
    )
    
    # Store document metadata in collection
    document_record = {
        "file_id": file_id,
        "filename": file.filename,
        "content_type": file.content_type or detected_type,
        "file_size": file_size,
        "upload_date": datetime.now(),
        "file_type": detected_type,
        "searchable_content": "",
        "tags": [],
        "description": "",
        "category": category
    }
    
    # If it's a text file, store searchable content
    if detected_type.startswith('text/') or file.filename.endswith(('.txt', '.md', '.json', '.csv')):
        try:
            searchable_content = file_content.decode('utf-8')
            document_record["searchable_content"] = searchable_content[:10000]  # Limit size
        except UnicodeDecodeError:
            logger.warning(f"Could not decode text content for {file.filename}")
    
    # Insert document record
    result = await database[COLLECTION_NAME].insert_one(document_record)
    
    return {
        "id": str(result.inserted_id),
        "filename": file.filename,
        "content_type": file.content_type or detected_type,
        "file_size": file_size,
        "upload_date": datetime.now().isoformat(),
        "file_type": detected_type,
        "category": category,
        "storage": "MongoDB"
    }

def store_file_local(file: UploadFile, file_content: bytes, file_size: int, detected_type: str, category: str = None):
    """Store file locally"""
    import uuid
    
    # Generate unique ID
    file_id = str(uuid.uuid4())
    
    # Save file locally
    file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
    with open(file_path, 'wb') as f:
        f.write(file_content)
    
    # Create metadata record
    document_record = {
        "id": file_id,
        "filename": file.filename,
        "content_type": file.content_type or detected_type,
        "file_size": file_size,
        "upload_date": datetime.now().isoformat(),
        "file_type": detected_type,
        "local_path": str(file_path),
        "category": category,
        "storage": "Local"
    }
    
    # Load existing metadata
    metadata = load_local_metadata()
    metadata.append(document_record)
    save_local_metadata(metadata)
    
    return {
        "id": file_id,
        "filename": file.filename,
        "content_type": file.content_type or detected_type,
        "file_size": file_size,
        "upload_date": datetime.now().isoformat(),
        "file_type": detected_type,
        "category": category,
        "storage": "Local"
    }

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...), category: Optional[str] = Form(None)):
    logger.info(f"Upload endpoint accessed with {len(files)} files")
    if category:
        logger.info(f"Upload category: {category}")
    
    uploaded_documents = []
    storage_mode = "MongoDB" if mongodb_connected else "Local Storage"
    
    for file in files:
        try:
            # Read file content
            file_content = await file.read()
            file_size = len(file_content)
            
            # Detect file type
            detected_type = detect_file_type(file_content, file.filename)
            
            # Log file details
            logger.info(f"Processing file: {file.filename}, detected_type: {detected_type}, size: {file_size}")
            
            # Store file based on available storage
            if mongodb_connected:
                document_info = await store_file_mongodb(file, file_content, file_size, detected_type, category)
            else:
                document_info = store_file_local(file, file_content, file_size, detected_type, category)
            
            uploaded_documents.append(document_info)
            
            logger.info(f"Successfully stored file: {file.filename} (Storage: {storage_mode})")
            
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing file {file.filename}: {str(e)}")
    
    logger.info(f"Upload completed successfully for {len(uploaded_documents)} files")
    
    return JSONResponse(
        content={
            "message": f"Successfully uploaded {len(uploaded_documents)} files ({storage_mode})",
            "documents": uploaded_documents,
            "storage_mode": storage_mode
        },
        status_code=200
    )

@app.get("/documents")
async def get_documents(
    limit: int = Query(20, description="Number of documents to return"),
    skip: int = Query(0, description="Number of documents to skip"),
    search: Optional[str] = Query(None, description="Search in filenames and content")
):
    """Get list of uploaded documents with optional search"""
    logger.info(f"Documents endpoint accessed with limit={limit}, skip={skip}, search={search}")
    
    try:
        if mongodb_connected:
            # MongoDB implementation
            query = {}
            if search:
                query = {
                    "$or": [
                        {"filename": {"$regex": search, "$options": "i"}},
                        {"searchable_content": {"$regex": search, "$options": "i"}},
                        {"description": {"$regex": search, "$options": "i"}}
                    ]
                }
            
            cursor = database[COLLECTION_NAME].find(query).sort("upload_date", -1).skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            document_list = []
            for doc in documents:
                upload_dt = doc["upload_date"]
                # Convert datetime to ISO string for JSON serialization
                if isinstance(upload_dt, datetime):
                    upload_dt = upload_dt.isoformat()
                document_list.append({
                    "id": str(doc["_id"]),
                    "filename": doc["filename"],
                    "content_type": doc["content_type"],
                    "file_size": doc["file_size"],
                    "upload_date": upload_dt,
                    "file_type": doc["file_type"],
                    "description": doc.get("description", ""),
                    "category": doc.get("category", "")
                })
            
            total_count = await database[COLLECTION_NAME].count_documents(query)
            
        else:
            # Local storage implementation
            metadata = load_local_metadata()
            
            # Apply search filter
            if search:
                metadata = [doc for doc in metadata if search.lower() in doc["filename"].lower()]
            
            # Sort by upload date (newest first)
            metadata.sort(key=lambda x: x["upload_date"], reverse=True)
            
            # Apply pagination
            total_count = len(metadata)
            document_list = metadata[skip:skip + limit]
            
            # Ensure upload_date is a string (ISO format) for JSON serialization
            # The metadata already stores ISO strings, so no conversion needed.
        
        logger.info(f"Returning {len(document_list)} documents (total: {total_count})")
        
        return JSONResponse(
            content={
                "message": f"Found {len(document_list)} documents",
                "documents": document_list,
                "total_count": total_count,
                "has_more": (skip + len(document_list)) < total_count,
                "storage_mode": "MongoDB" if mongodb_connected else "Local Storage"
            },
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Error retrieving documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")

@app.get("/documents/{document_id}")
async def get_document(document_id: str):
    """Get a specific document by ID"""
    logger.info(f"Document download endpoint accessed for ID: {document_id}")
    
    try:
        if mongodb_connected:
            # MongoDB implementation
            document = await database[COLLECTION_NAME].find_one({"_id": ObjectId(document_id)})
        else:
            # Local storage implementation
            metadata = load_local_metadata()
            document = next((doc for doc in metadata if doc["id"] == document_id), None)

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if mongodb_connected:
            # Get file from GridFS
            file_id = document["file_id"]
            grid_out = await fs_bucket.open_download_stream(file_id)
        else:
            # Get file from local storage
            file_path = Path(document["local_path"])
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="Document not found locally")
            grid_out = open(file_path, 'rb')
        
        # Read file content
        file_content = await grid_out.read()
        
        logger.info(f"Document retrieved successfully: {document['filename']}")
        
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type=document["content_type"],
            headers={
                "Content-Disposition": f"attachment; filename={document['filename']}",
                "Content-Length": str(document["file_size"])
            }
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format")
    except Exception as e:
        logger.error(f"Error retrieving document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(e)}")

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a specific document by ID"""
    logger.info(f"Document deletion endpoint accessed for ID: {document_id}")
    
    try:
        if mongodb_connected:
            # MongoDB implementation
            document = await database[COLLECTION_NAME].find_one({"_id": ObjectId(document_id)})
        else:
            # Local storage implementation
            metadata = load_local_metadata()
            document = next((doc for doc in metadata if doc["id"] == document_id), None)

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if mongodb_connected:
            # Delete file from GridFS
            file_id = document["file_id"]
            await fs_bucket.delete(file_id)
        else:
            # Delete file from local storage
            file_path = Path(document["local_path"])
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted local file: {file_path}")
        
        # Delete document record
        if mongodb_connected:
            await database[COLLECTION_NAME].delete_one({"_id": ObjectId(document_id)})
        else:
            metadata = load_local_metadata()
            metadata = [doc for doc in metadata if doc["id"] != document_id]
            save_local_metadata(metadata)
        
        logger.info(f"Document deleted successfully: {document['filename']}")
        
        return JSONResponse(
            content={
                "message": f"Document '{document['filename']}' deleted successfully"
            },
            status_code=200
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID format")
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@app.post("/cleanup")
async def cleanup_orphaned_files():
    """Clean up any orphaned files that exist in uploads directory but not in metadata"""
    logger.info("Cleanup endpoint accessed")
    
    try:
        if mongodb_connected:
            # For MongoDB, we'd need to check GridFS vs collection records
            # This is more complex and would require additional implementation
            return JSONResponse(
                content={"message": "Cleanup not implemented for MongoDB mode yet"},
                status_code=501
            )
        else:
            # Local storage cleanup
            metadata = load_local_metadata()
            
            # Get all files currently in metadata
            metadata_files = set()
            for doc in metadata:
                if 'local_path' in doc:
                    file_path = Path(doc['local_path'])
                    metadata_files.add(file_path.name)
            
            # Get all files in uploads directory
            upload_files = set()
            for file_path in UPLOAD_DIR.glob("*"):
                if file_path.is_file() and file_path.name != "metadata.json":
                    upload_files.add(file_path.name)
            
            # Find orphaned files (in directory but not in metadata)
            orphaned_files = upload_files - metadata_files
            
            # Remove orphaned files
            removed_files = []
            for orphaned_file in orphaned_files:
                file_path = UPLOAD_DIR / orphaned_file
                if file_path.exists():
                    file_path.unlink()
                    removed_files.append(orphaned_file)
                    logger.info(f"Removed orphaned file: {orphaned_file}")
            
            # Find missing files (in metadata but not in directory)
            missing_files = metadata_files - upload_files
            
            # Remove metadata entries for missing files
            if missing_files:
                original_count = len(metadata)
                metadata = [doc for doc in metadata 
                           if 'local_path' not in doc or 
                           Path(doc['local_path']).name not in missing_files]
                
                if len(metadata) != original_count:
                    save_local_metadata(metadata)
                    logger.info(f"Removed {original_count - len(metadata)} metadata entries for missing files")
            
            logger.info(f"Cleanup completed: {len(removed_files)} orphaned files removed, {len(missing_files)} missing file entries cleaned")
            
            return JSONResponse(
                content={
                    "message": "Cleanup completed successfully",
                    "orphaned_files_removed": len(removed_files),
                    "missing_file_entries_cleaned": len(missing_files),
                    "removed_files": removed_files,
                    "missing_files": list(missing_files)
                },
                status_code=200
            )
        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during cleanup: {str(e)}")

@app.get("/documents/stats")
async def get_document_stats():
    """Get statistics about stored documents"""
    logger.info("Document stats endpoint accessed")
    
    try:
        if mongodb_connected:
            # MongoDB implementation
            total_count = await database[COLLECTION_NAME].count_documents({})
            
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "total_size": {"$sum": "$file_size"},
                        "avg_size": {"$avg": "$file_size"}
                    }
                }
            ]
            
            size_stats = await database[COLLECTION_NAME].aggregate(pipeline).to_list(length=1)
            
            type_pipeline = [
                {
                    "$group": {
                        "_id": "$file_type",
                        "count": {"$sum": 1}
                    }
                },
                {"$sort": {"count": -1}}
            ]
            
            type_stats = await database[COLLECTION_NAME].aggregate(type_pipeline).to_list(length=None)
            
            stats = {
                "total_documents": total_count,
                "total_size_bytes": size_stats[0]["total_size"] if size_stats else 0,
                "average_size_bytes": size_stats[0]["avg_size"] if size_stats else 0,
                "file_types": type_stats,
                "storage_mode": "MongoDB"
            }
            
        else:
            # Local storage implementation
            metadata = load_local_metadata()
            
            total_count = len(metadata)
            total_size = sum(doc["file_size"] for doc in metadata)
            avg_size = total_size / total_count if total_count > 0 else 0
            
            # File type distribution
            type_counts = {}
            for doc in metadata:
                file_type = doc["file_type"]
                type_counts[file_type] = type_counts.get(file_type, 0) + 1
            
            type_stats = [{"_id": k, "count": v} for k, v in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)]
            
            stats = {
                "total_documents": total_count,
                "total_size_bytes": total_size,
                "average_size_bytes": avg_size,
                "file_types": type_stats,
                "storage_mode": "Local Storage"
            }
        
        logger.info(f"Document stats retrieved: {stats['total_documents']} documents")
        
        return JSONResponse(content=stats, status_code=200)
        
    except Exception as e:
        logger.error(f"Error retrieving document stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving stats: {str(e)}")

@app.get("/knowledge-graph")
async def get_knowledge_graph():
    """
    Returns the knowledge graph as a JSON object suitable for D3.js visualization.
    """
    logger.info("Knowledge graph endpoint accessed")
    
    try:
        kg = KnowledgeGraph()
        
        # Try to load existing graph, if not found create a new one with examples
        try:
            kg.load("knowledge_graph.pkl")
            logger.info("Loaded existing knowledge graph")
        except Exception as e:
            logger.info(f"No existing graph found, creating new one: {e}")
            # Create example data as in the original script
            kg.add_entry("Knowledge", "What is your expertise?", "AI, coding, philosophy")
            kg.add_entry("Feelings", "How do you feel today?", "Curious and motivated")
            kg.add_entry("Personalities", "Which of the Big Five fits you best?", "Openness to experience")
            kg.add_entry("ImportanceOfPeople", "Who is most important in your life?", "Family and close friends")
            kg.add_entry("Preferences", "What is your favorite hobby?", "Reading science fiction")
            kg.add_entry("Morals", "Is honesty always the best policy?", "Usually, but context matters")
            kg.add_entry("AutomaticQuestions", "What would you like to learn next?", "Graph databases")
            kg.save("knowledge_graph.pkl")
            logger.info("Created and saved new knowledge graph with example data")
        
        G = kg.graph
        nodes = []
        for node, data in G.nodes(data=True):
            node_data = {"id": node}
            node_data.update(data)
            nodes.append(node_data)
        
        links = []
        for source, target, data in G.edges(data=True):
            link = {"source": source, "target": target}
            link.update(data)
            links.append(link)
        
        result = {"nodes": nodes, "links": links}
        logger.info(f"Returning knowledge graph with {len(nodes)} nodes and {len(links)} links")
        
        return JSONResponse(content=result, status_code=200)
        
    except Exception as e:
        logger.error(f"Error retrieving knowledge graph: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving knowledge graph: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting FastAPI server on port 8089...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8089,
        reload=True,
        log_level="info"
    ) 