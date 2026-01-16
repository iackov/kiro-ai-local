"""
RAG Engine - Core logic for document processing and retrieval
"""
import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import structlog
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader
)

logger = structlog.get_logger()


class RAGEngine:
    def __init__(self, ollama_url: str, chroma_url: str):
        self.ollama_url = ollama_url
        self.chroma_url = chroma_url
        self.chroma_client = None
        self.collection = None
        
        # Text splitter for semantic chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    async def initialize(self):
        """Initialize ChromaDB connection"""
        try:
            # Use PersistentClient for simplicity (no HTTP needed)
            import chromadb
            from chromadb.config import Settings
            
            self.chroma_client = chromadb.PersistentClient(
                path="/chroma/chroma",
                settings=Settings(
                    anonymized_telemetry=False
                )
            )
            
            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name="rag_documents",
                metadata={"description": "RAG document store"}
            )
            
            logger.info("chromadb_initialized", collection=self.collection.name)
        except Exception as e:
            logger.error("chromadb_init_failed", error=str(e))
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all services"""
        services = {}
        
        # Check ChromaDB
        try:
            # Use v2 API
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.chroma_url}/api/v2/heartbeat", timeout=5.0)
                services["chromadb"] = "healthy" if response.status_code == 200 else "unhealthy"
        except:
            services["chromadb"] = "unhealthy"
        
        # Check Ollama
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.ollama_url}/api/tags", timeout=5.0)
                services["ollama"] = "healthy" if response.status_code == 200 else "unhealthy"
        except:
            services["ollama"] = "unhealthy"
        
        status = "healthy" if all(v == "healthy" for v in services.values()) else "degraded"
        
        return {
            "status": status,
            "services": services
        }
    
    async def query(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query the vector database"""
        start_time = time.time()
        
        try:
            # Use Ollama for embeddings via ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where=filters
            )
            
            documents = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    documents.append({
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "score": results["distances"][0][i] if results["distances"] else 0.0
                    })
            
            processing_time = (time.time() - start_time) * 1000
            
            return {
                "query": query,
                "documents": documents,
                "total_results": len(documents),
                "processing_time_ms": processing_time
            }
        except Exception as e:
            logger.error("query_failed", error=str(e))
            raise
    
    async def ingest_path(
        self,
        path: str,
        recursive: bool = True,
        file_types: List[str] = None
    ) -> Dict[str, Any]:
        """Ingest documents from a path"""
        if file_types is None:
            file_types = [".pdf", ".md", ".txt", ".py", ".js", ".ts", ".json"]
        
        files_processed = 0
        chunks_created = 0
        errors = []
        
        path_obj = Path(path)
        
        if not path_obj.exists():
            raise ValueError(f"Path does not exist: {path}")
        
        # Collect files
        files_to_process = []
        if path_obj.is_file():
            files_to_process = [path_obj]
        else:
            pattern = "**/*" if recursive else "*"
            for file_type in file_types:
                files_to_process.extend(path_obj.glob(f"{pattern}{file_type}"))
        
        # Process each file
        for file_path in files_to_process:
            try:
                result = await self.ingest_file(str(file_path))
                files_processed += 1
                chunks_created += result.get("chunks_created", 0)
            except Exception as e:
                errors.append(f"{file_path}: {str(e)}")
                logger.error("file_ingest_failed", file=str(file_path), error=str(e))
        
        return {
            "success": len(errors) == 0,
            "files_processed": files_processed,
            "chunks_created": chunks_created,
            "errors": errors
        }
    
    async def ingest_file(self, file_path: str) -> Dict[str, Any]:
        """Ingest a single file"""
        file_path_obj = Path(file_path)
        extension = file_path_obj.suffix.lower()
        
        # Load document based on type
        try:
            if extension == ".pdf":
                loader = PyPDFLoader(file_path)
            elif extension in [".md", ".txt"]:
                # Use simple TextLoader for markdown and text
                loader = TextLoader(file_path, encoding='utf-8')
            else:
                loader = TextLoader(file_path, encoding='utf-8')
            
            documents = loader.load()
        except Exception as e:
            logger.error("file_load_failed", file=file_path, error=str(e))
            raise ValueError(f"Failed to load file: {str(e)}")
        
        # Split into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Prepare for ChromaDB
        texts = [chunk.page_content for chunk in chunks]
        metadatas = [
            {
                **chunk.metadata,
                "source": file_path,
                "chunk_index": i
            }
            for i, chunk in enumerate(chunks)
        ]
        ids = [f"{file_path}_{i}" for i in range(len(chunks))]
        
        # Add to collection
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info("file_ingested", file=file_path, chunks=len(chunks))
        
        return {
            "success": True,
            "chunks_created": len(chunks)
        }
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        count = self.collection.count()
        return {
            "total_documents": count,
            "collection_name": self.collection.name
        }
    
    async def clear(self) -> Dict[str, Any]:
        """Clear all documents"""
        self.chroma_client.delete_collection(self.collection.name)
        self.collection = self.chroma_client.create_collection(
            name="rag_documents",
            metadata={"description": "RAG document store"}
        )
        return {"success": True, "message": "Database cleared"}
