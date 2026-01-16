"""
RAG API Service - Document ingestion, chunking, and retrieval
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import structlog
import os

from rag_engine import RAGEngine
from models import QueryRequest, QueryResponse, IngestRequest, IngestResponse, HealthResponse

# Initialize structured logging
logger = structlog.get_logger()

# Initialize FastAPI
app = FastAPI(
    title="RAG API",
    description="Structured Semantic API for document ingestion and retrieval",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG engine
rag_engine = RAGEngine(
    ollama_url=os.getenv("OLLAMA_URL", "http://ollama:11434"),
    chroma_url=os.getenv("CHROMA_URL", "http://chromadb:8000")
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting RAG API service")
    await rag_engine.initialize()
    logger.info("RAG API service ready")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    status = await rag_engine.health_check()
    return HealthResponse(**status)


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Query the RAG system with semantic search
    """
    try:
        logger.info("query_received", query=request.query, top_k=request.top_k)
        
        results = await rag_engine.query(
            query=request.query,
            top_k=request.top_k,
            filters=request.filters
        )
        
        logger.info("query_completed", num_results=len(results.get("documents", [])))
        return QueryResponse(**results)
        
    except Exception as e:
        logger.error("query_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest", response_model=IngestResponse)
async def ingest(request: IngestRequest):
    """
    Ingest documents from a path (supports PDF, Markdown, Code)
    """
    try:
        logger.info("ingest_started", path=request.path, recursive=request.recursive)
        
        result = await rag_engine.ingest_path(
            path=request.path,
            recursive=request.recursive,
            file_types=request.file_types
        )
        
        logger.info("ingest_completed", **result)
        return IngestResponse(**result)
        
    except Exception as e:
        logger.error("ingest_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/upload")
async def ingest_upload(file: UploadFile = File(...)):
    """
    Upload and ingest a single file
    """
    try:
        logger.info("upload_received", filename=file.filename)
        
        # Save uploaded file
        upload_path = f"/data/uploads/{file.filename}"
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        
        with open(upload_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Ingest the file
        result = await rag_engine.ingest_file(upload_path)
        
        logger.info("upload_completed", filename=file.filename, chunks=result.get("chunks_created", 0))
        return result
        
    except Exception as e:
        logger.error("upload_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/inspect")
async def inspect():
    """
    Inspect the current state of the vector database
    """
    try:
        stats = await rag_engine.get_stats()
        return stats
    except Exception as e:
        logger.error("inspect_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/clear")
async def clear_database():
    """
    Clear all documents from the vector database (use with caution)
    """
    try:
        logger.warning("clear_database_requested")
        result = await rag_engine.clear()
        logger.info("clear_database_completed")
        return result
    except Exception as e:
        logger.error("clear_database_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
