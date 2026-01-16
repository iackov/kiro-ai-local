"""
Pydantic models for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query")
    top_k: int = Field(5, ge=1, le=50, description="Number of results to return")
    filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")


class DocumentResult(BaseModel):
    content: str
    metadata: Dict[str, Any]
    score: float


class QueryResponse(BaseModel):
    query: str
    documents: List[DocumentResult]
    total_results: int
    processing_time_ms: float


class IngestRequest(BaseModel):
    path: str = Field(..., description="Path to ingest (file or directory)")
    recursive: bool = Field(True, description="Recursively process directories")
    file_types: Optional[List[str]] = Field(
        [".pdf", ".md", ".txt", ".py", ".js", ".ts", ".json"],
        description="File extensions to process"
    )


class IngestResponse(BaseModel):
    success: bool
    files_processed: int
    chunks_created: int
    errors: List[str] = []


class HealthResponse(BaseModel):
    status: str
    services: Dict[str, str]
    version: str = "1.0.0"
