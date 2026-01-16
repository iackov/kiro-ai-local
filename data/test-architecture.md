# AI Combiner Architecture

## Overview
The AI Combiner is a modular system for local AI operations.

## Components

### Ollama
Ollama provides local LLM inference. It runs models like llama2 and nomic-embed-text.
The service listens on port 11434 and stores models in a persistent volume.

### RAG API
The RAG API is built with FastAPI and handles document ingestion and retrieval.
It uses ChromaDB for vector storage and semantic search.
The API exposes endpoints for query, ingest, and inspect operations.

### MCP Gateway
MCP Gateway acts as a proxy between Kiro IDE and the RAG API.
It provides a simplified REST interface for integration.

## Data Flow
1. Documents are ingested through the RAG API
2. Text is split into chunks with overlap
3. Chunks are embedded using Ollama
4. Embeddings are stored in ChromaDB
5. Queries retrieve relevant chunks via semantic search
