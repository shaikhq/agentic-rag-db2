# Agentic RAG with IBM Db2

This repository demonstrates how to build an **agentic Retrieval-Augmented Generation (RAG)** workflow using IBM Db2 and the `langchain-db2` connector. The project begins with a prototype in a Jupyter notebook and evolves into a modular, production-aligned implementation with separate microservices.

## Project Structure

```
agentic-rag-db2/
├── prototype/
├── ingestion-api/
├── search-api/
├── models/
├── README.md
└── .env
```

### `prototype/`

A single-notebook prototype that implements the full agentic RAG pipeline:

* Loads and chunks documents
* Embeds them using a local LLM (`llama.cpp`)
* Stores vectors in Db2 using `langchain-db2`
* Performs semantic retrieval
* Uses LangGraph to rewrite queries and guide agent decisions

This is intended as a reference implementation to experiment with the overall workflow end-to-end.

### `ingestion-api/`

A FastAPI microservice that handles document ingestion and vector storage. This service extracts the document processing logic from the prototype and exposes it as a REST API. Features include:

* Web document extraction from URLs using Trafilatura
* Intelligent text chunking with sentence-aware splitting
* Local embedding generation using Granite models
* Vector storage in Db2's vector database
* Table management (create, clear, validate)
* Health monitoring and error handling

**Port:** 8001  
Refer to `ingestion-api/README.md` for setup instructions and API usage.

### `search-api/`

A minimalistic FastAPI microservice that provides intelligent question-answering using Agentic RAG. This service implements a multi-step reasoning workflow orchestrated by LangGraph:

* Semantic document retrieval from Db2 vector database
* Document relevance grading using IBM Watsonx
* Automatic query rewriting for improved results
* Context-aware answer generation
* Fallback mechanisms for robust operation

**Port:** 8002  
Refer to `search-api/README.md` for setup instructions and API usage.

### `models/`

Shared directory containing local AI models:

* **Granite Embedding Model**: `granite-embedding-30m-english-Q6_K.gguf` for semantic search
* **Language Models**: Additional models as needed for local inference

Both APIs share these models to ensure consistency and reduce storage overhead.

## Architecture

The system follows a microservices architecture:

1. **Document Ingestion Pipeline**: `ingestion-api` processes web documents into searchable vectors
2. **Intelligent Search**: `search-api` uses agentic workflows to provide accurate, context-aware answers
3. **Shared Resources**: Common database, models, and configuration via `.env`

## Quick Start

### Prerequisites

* Python 3.13+
* UV package manager
* IBM Db2 database with vector support
* IBM Watsonx account (for search API)

### Setup

1. **Configure environment**:
   ```bash
   # Create .env file in root directory
   cp .env.example .env
   # Edit .env with your credentials
   ```

2. **Download models**:
   ```bash
   mkdir -p models
   wget -O models/granite-embedding-30m-english-Q6_K.gguf \
     https://huggingface.co/lmstudio-community/granite-embedding-30m-english-GGUF/resolve/main/granite-embedding-30m-english-Q6_K.gguf
   ```

3. **Start ingestion service**:
   ```bash
   cd ingestion-api
   uv sync
   uv run uvicorn ingestion_api:app --reload --host 0.0.0.0 --port 8001
   ```

4. **Start search service**:
   ```bash
   cd search-api
   uv sync
   uv run uvicorn search_api:app --reload --host 0.0.0.0 --port 8002
   ```

### Usage Example

```bash
# 1. Ingest a document
curl -X POST "http://localhost:8001/ingest" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article", "table_name": "AI_KNOWLEDGE"}'

# 2. Search and get answers
curl -X POST "http://localhost:8002/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic?", "table_name": "AI_KNOWLEDGE"}'
```

## Roadmap

This repo is evolving from a prototype to a set of deployable services. Planned enhancements:

* **Observability**: Logging, metrics, and tracing
* **Authentication**: API security and access control
* **Scalability**: Horizontal scaling and load balancing
* **UI Interface**: Web frontend for document management and search
* **Advanced RAG**: Multi-modal content, citation tracking, and source verification

## Development

To try out the prototype:

```bash
cd prototype/
# Open and run agent.ipynb in Jupyter
```

To develop the APIs:

```bash
# Each service has its own UV environment
cd ingestion-api/ && uv sync
cd search-api/ && uv sync
```

## About

This project demonstrates how AI agents can interact with structured and unstructured data using relational databases like IBM Db2. It combines vector search, local embeddings, IBM Watsonx AI, and LangGraph-based query refinement into a cohesive, production-ready RAG pipeline.

The modular architecture allows for independent scaling, testing, and deployment of ingestion and search capabilities while maintaining consistency through shared models and database infrastructure.