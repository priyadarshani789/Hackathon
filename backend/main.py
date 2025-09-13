from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import openai
from services.parser import parse_document
from services.linter import run_all_checks
from services.scorer import calculate_score
from services.embedding_service import EmbeddingService, process_and_store_document
from config.config import (
    validate_config, 
    AZURE_CHAT_ENDPOINT, 
    AZURE_CHAT_API_KEY,
    AZURE_CHAT_API_VERSION,
    AZURE_CHAT_DEPLOYMENT,
    AZURE_EMBEDDING_DEPLOYMENT,
    HOST,
    PORT,
    DEBUG
)

# Validate configuration on startup
try:
    validate_config()
    print("✅ Configuration validated")
except ValueError as e:
    print(f"❌ Configuration error: {e}")
    exit(1)

# Initialize the Azure OpenAI client
client = openai.AzureOpenAI(
    azure_endpoint=AZURE_CHAT_ENDPOINT,
    api_version=AZURE_CHAT_API_VERSION,
    api_key=AZURE_CHAT_API_KEY
)

# Create FastAPI application
app = FastAPI(
    title="GxP Compliance Assistant API", 
    description="AI-powered document compliance analysis for GxP regulations",
    version="1.0.0"
)

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # React development server
        "http://localhost:5173",    # Vite development server
        "http://127.0.0.1:5173",    # Vite alternative
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """Root endpoint for health check"""
    return {
        "message": "GxP Compliance Assistant API is running",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.post("/analyze-sop/")
def analyze_sop(file: UploadFile = File(...)):
    """Analyze an SOP document for compliance issues and store embeddings."""
    try:
        # Check file extension
        if not (file.filename.endswith('.docx') or file.filename.endswith('.pdf')):
            raise HTTPException(status_code=400, detail="Only DOCX and PDF files are supported")
        
        # Read file content and parse document
        file_content = file.file.read()
        parsed_data = parse_document(file_content, file.filename)
        
        # Store embeddings in ChromaDB
        try:
            embedding_result = process_and_store_document(parsed_data, file.filename)
        except Exception as e:
            embedding_result = {"status": "failed", "error": str(e)}
        
        # Run compliance checks
        findings = run_all_checks(
            parsed_data=parsed_data,
            client=client,
            chat_deployment=AZURE_CHAT_DEPLOYMENT,
            embedding_deployment=AZURE_EMBEDDING_DEPLOYMENT
        )
        
        # Calculate compliance score
        score = calculate_score(findings)
        
        return {
            "score": score,
            "findings": findings,
            "document_info": {
                "filename": file.filename,
                "sections_found": len(parsed_data.get("sections", {})),
                "metadata": parsed_data.get("metadata", {})
            },
            "embedding_info": embedding_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "azure_openai_configured": bool(AZURE_CHAT_API_KEY),
        "endpoint": AZURE_CHAT_ENDPOINT,
        "chat_deployment": AZURE_CHAT_DEPLOYMENT,
        "embedding_deployment": AZURE_EMBEDDING_DEPLOYMENT
    }

@app.get("/api/config")
def get_config():
    """Get API configuration status (without sensitive data)"""
    return {
        "chat_model_configured": bool(AZURE_CHAT_API_KEY),
        "embedding_model_configured": bool(AZURE_CHAT_API_KEY),  # Using same key
        "supported_formats": ["docx", "pdf"],
        "api_version": "1.0.0"
    }

@app.get("/api/documents/stats")
def get_document_stats():
    """Get statistics about stored documents in ChromaDB."""
    try:
        embedding_service = EmbeddingService()
        stats = embedding_service.get_collection_stats()
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting document stats: {e}")

@app.post("/api/documents/search")
def search_documents(query: dict):
    """Search documents in ChromaDB using semantic similarity."""
    try:
        search_query = query.get("query", "")
        n_results = query.get("n_results", 5)
        
        if not search_query:
            raise HTTPException(status_code=400, detail="Search query is required")
        
        embedding_service = EmbeddingService()
        results = embedding_service.search_similar_documents(search_query, n_results)
        
        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documents: {e}")

@app.delete("/api/documents/{document_id}")
def delete_document(document_id: str):
    """Delete a document and all its chunks from ChromaDB."""
    try:
        embedding_service = EmbeddingService()
        success = embedding_service.delete_document(document_id)
        
        if success:
            return {
                "status": "success",
                "message": f"Document {document_id} deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Document not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {e}")

@app.get("/api/documents/{document_id}/chunks")
def get_document_chunks(document_id: str):
    """Get all chunks for a specific document."""
    try:
        embedding_service = EmbeddingService()
        chunks = embedding_service.get_document_chunks(document_id)
        
        return {
            "status": "success",
            "document_id": document_id,
            "chunks": chunks,
            "total_chunks": len(chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting document chunks: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT, reload=DEBUG)
