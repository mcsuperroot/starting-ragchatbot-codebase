# AGENTS.md - Development Guide for Agentic AI

## Project Overview

- **Python**: 3.12+ (3.13 not supported due to onnxruntime)
- **Package Manager**: uv
- **Framework**: FastAPI with ChromaDB (vector store) and Groq (AI)
- **Default Model**: llama-3.3-70b-versatile
- **Quick Start**: `uv sync --python 3.12 && ./run.sh`

---

## Build, Run & Test Commands

### Installation
```bash
uv sync --python 3.12     # Install dependencies with Python 3.12
uv sync --frozen --python 3.12  # Reproducible install (lock file only)
```

### Running the Application
```bash
./run.sh                 # Quick start (creates docs dir + starts server)
cd backend && uv run --python 3.12 uvicorn app:app --reload --port 9000  # Manual
```

### Environment Variables
Create `.env` in project root:
```bash
GROQ_API_KEY=your-groq-api-key-here
```

### Testing (pytest)
```bash
uv add --dev pytest pytest-asyncio   # Install pytest (if not present)

uv run pytest                    # Run all tests
uv run pytest tests/            # Run tests in directory
uv run pytest tests/test_x.py   # Run specific file
uv run pytest -k "test_name"   # Run tests matching pattern
uv run pytest tests/test_x.py::test_function  # Run single test function
uv run pytest -v                # Verbose output
uv run pytest --tb=short        # Short traceback
```

### Linting & Formatting (ruff)
```bash
uv add --dev ruff   # Install ruff (replaces isort + flake8)

uv run ruff check .              # Lint all files
uv run ruff check --fix .        # Lint + auto-fix
uv run ruff format .             # Format code
uv run ruff check --watch .      # Watch mode
```

### Recommended pyproject.toml additions

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
asyncio_mode = "auto"
addopts = "-v --tb=short"

[tool.ruff]
target-version = "py313"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
ignore = ["E501"]  # line-too-long handled by formatter
fixable = ["ALL"]
```

---

## Code Style Guidelines

### Imports
Group in this order, separate with blank line, sort alphabetically within groups:
```python
# Standard library
import os
import re
from typing import Dict, List, Optional, Tuple

# Third-party
import chromadb
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

# Local application
from config import config
from models import Course, Lesson
```

### Type Hints
Required for function parameters and return types:
```python
# Good
def query(self, query: str, session_id: Optional[str] = None) -> Tuple[str, List[str]]:
    ...

# Use Optional[T] not T | None
def process(query: Optional[str] = None) -> str | None:  # Avoid
def process(query: Optional[str] = None) -> Optional[str]:  # Preferred
```

### Naming Conventions
| Element | Convention | Example |
|---------|------------|---------|
| Classes | PascalCase | `VectorStore`, `RAGSystem` |
| Functions/variables | snake_case | `query_documents`, `session_id` |
| Constants | SCREAMING_SNAKE_CASE | `MAX_RESULTS`, `CHUNK_SIZE` |
| Private methods | prefix `_` | `_resolve_course_name` |
| Private variables | prefix `_` | `_sessions` |
| Type aliases | PascalCase | `SearchResults`, `CourseStats` |

### Data Models
- **Pydantic `BaseModel`**: API request/response schemas
- **`@dataclass`**: Simple DTOs, configuration objects
- **`@dataclass` + ABC**: Abstract base classes for interfaces
```python
# API models (Pydantic)
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

# DTOs (dataclass)
@dataclass
class Message:
    role: str
    content: str

# Abstract base (dataclass + ABC)
@dataclass
class Tool(ABC):
    @abstractmethod
    def execute(self, **kwargs) -> str:
        pass
```

### Docstrings
Google-style for public methods:
```python
def search(self, query: str, limit: int = 5) -> SearchResults:
    """
    Search course content by query.

    Args:
        query: The search query string.
        limit: Maximum number of results to return.

    Returns:
        SearchResults object containing documents and metadata.

    Raises:
        ValueError: If query is empty.
    """
```

### Error Handling
- Catch specific exceptions, avoid bare `except:`
- Return empty results with error message (preferred pattern)
- Raise `HTTPException` for API endpoints
```python
# Good - return error with results
@dataclass
class SearchResults:
    error: Optional[str] = None
    
    @classmethod
    def empty(cls, error_msg: str) -> 'SearchResults':
        return cls(documents=[], metadata=[], distances=[], error=error_msg)

# Good - API error handling
@app.post("/api/query")
async def query_documents(request: QueryRequest):
    try:
        ...
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Async Patterns
- Use `async def` for all FastAPI endpoints
- Use `await` for I/O operations
- Thread pool for CPU-bound operations if needed

---

## Project Structure

```
backend/
├── app.py              # FastAPI app, endpoints, CORS middleware
├── config.py           # @dataclass Config with env vars
├── models.py           # Pydantic models (API schemas)
├── vector_store.py     # ChromaDB wrapper, SearchResults dataclass
├── rag_system.py       # Main orchestrator, coordinates components
├── ai_generator.py     # Anthropic Claude client, tool execution
├── document_processor.py  # Parses course docs, chunks text
├── session_manager.py  # Conversation history, session state
├── search_tools.py     # Tool ABC, CourseSearchTool, ToolManager

frontend/
├── index.html          # Main UI
├── script.js           # Frontend logic
├── style.css           # Styles

docs/                   # Course documents (txt, pdf, docx)
.env                    # Environment variables (API keys)
```

---

## Development Notes

### Environment Variables
Create `.env` in project root:
```bash
GROQ_API_KEY=your-groq-api-key-here
```
Never commit `.env` files.

### ChromaDB Storage
- Location: `backend/chroma_db/`
- Two collections: `course_catalog` (metadata), `course_content` (chunks)
- Cleared via `VectorStore.clear_all_data()`

### Document Format
Course documents support this format:
```
Course Title: Course Name
Course Link: https://example.com
Course Instructor: Instructor Name

Lesson 1: Introduction
Lesson Link: https://example.com/lesson1
Content goes here...

Lesson 2: Getting Started
Content for lesson 2...
```

### Adding New Tools
1. Create tool class inheriting from `Tool` ABC
2. Implement `get_tool_definition()` and `execute()`
3. Register with `tool_manager.register_tool(your_tool)`

### API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/query` | Query course materials |
| GET | `/api/courses` | Get course statistics |
| GET | `/` | Serve frontend (static files) |

---

## Testing Recommendations

### Test Structure
```
tests/
├── conftest.py              # Shared fixtures
├── test_rag_system.py       # Integration tests
├── test_vector_store.py     # Unit tests
├── test_ai_generator.py     # Mock tests
└── test_api.py              # API endpoint tests
```

### Example conftest.py
```python
import pytest
from config import Config
from rag_system import RAGSystem

@pytest.fixture
def config():
    return Config(ANTHROPIC_API_KEY="test-key")

@pytest.fixture
def rag_system(config):
    return RAGSystem(config)
```

### Mocking Claude API
```python
from unittest.mock import Mock, patch

def test_ai_response():
    with patch('anthropic.Anthropic') as mock_client:
        mock_client.return_value.messages.create.return_value = Mock(
            content=[Mock(text="Test response")],
            stop_reason="end_turn"
        )
        # ... test code
```
