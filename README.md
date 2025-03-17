# RAG-based Chatbot with Ollama and Qdrant

A chatbot implementation using RAG (Retrieval-Augmented Generation) architecture, powered by Ollama for LLM capabilities and Qdrant for vector storage.

## Project Structure

```
.
├── data/                  # Data storage directory
│   └── qdrant_data/         # Qdrant vector database storage
├── models/                # Model storage directory
│   └── ollama/            # Ollama model files and configurations
├── src/                   # Source code directory
│   ├── database/          # Database connection and operations
│   ├── handlers/          # Request handlers and business logic
│   ├── helpers/           # Helper functions and utilities
│   ├── routers/           # FastAPI route definitions
│   ├── schemas/           # Pydantic models and schemas
│   ├── settings/          # Configuration and environment settings
│   └── utils/             # Utility functions and common tools
├── docker-compose.yml     # Docker compose configuration
├── Dockerfile             # Docker build instructions
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## Directory Functions

### Source Code (`src/`)
- `database/`: Database connection management and CRUD operations
- `handlers/`: Business logic implementation and request processing
- `helpers/`: Common helper functions and shared utilities
- `routers/`: API endpoint definitions and route handlers
- `schemas/`: Data validation and serialization models
- `settings/`: Application configuration and environment variables
- `utils/`: General utility functions and tools

### Data Storage (`data/`)
- `qdrant_data/`: Persistent storage for Qdrant vector database
  - Stores document embeddings
  - Maintains index information
  - Handles vector similarity search

### Models (`models/`)
- `ollama/`: Storage for Ollama LLM files
  - Model weights and configurations
  - Custom model definitions
  - Model cache

## Key Components

### 1. Qdrant Vector Database
- Manages vector embeddings for document retrieval
- Provides efficient similarity search capabilities
- Persists data in `data/qdrant_data/`

### 2. Ollama LLM Service
- Handles text generation and completion
- Processes natural language queries
- GPU-accelerated inference

### 3. FastAPI Application
- RESTful API implementation
- Handles client requests
- Coordinates between Qdrant and Ollama services

## Setup and Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start services with Docker Compose:
   ```bash
   docker-compose up -d
   ```

## Environment Variables

Create a `.env` file with the following variables:
```
OLLAMA_API_URL=http://ollama:11434
QDRANT_HOST=qdrant
QDRANT_PORT=6333
```

## API Endpoints

The service exposes the following endpoints:
- `POST /chat`: Send messages to the chatbot
- `POST /documents`: Upload documents for RAG processing
- `GET /health`: Service health check

## Development

1. Start the development server:
   ```bash
   uvicorn src.main:app --reload
   ```

2. Access the API documentation:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## Docker Support

The application is containerized with Docker:
- Qdrant container for vector storage
- Ollama container for LLM processing
- FastAPI application container

Use `docker-compose up` to start all services.

## License

[Your License Here]
