# Multi-Agent Boilerplate Template

A production-ready, extensible boilerplate for building AI agent systems with FastAPI, vector databases, and LLM integration. This template provides a structured approach to creating intelligent agents that can process data, make decisions, and integrate with various data stores.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🎯 Overview

This boilerplate template demonstrates a real-world implementation of an AI agent system for case similarity detection and clustering. It showcases best practices for building scalable, maintainable, and production-ready agent-based applications.

### Key Highlights

- **Modular Agent Architecture**: Easily extendable base agent class for creating specialized agents
- **Vector Database Integration**: Built-in Qdrant support for semantic search and similarity detection
- **LLM Integration**: Seamless integration with OpenAI, Claude, Gemini, and custom LLM providers
- **Production-Ready API**: FastAPI-based REST API with comprehensive error handling
- **Configuration Management**: Centralized settings with environment variable support
- **Async/Await Support**: Fully asynchronous for high-performance operations
- **Type Safety**: Pydantic models throughout for data validation

## 📋 Table of Contents

- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Core Concepts](#core-concepts)
- [Getting Started](#getting-started)
- [Creating Your Own Agent](#creating-your-own-agent)
- [API Usage](#api-usage)
- [Configuration](#configuration)
- [Database Services](#database-services)
- [Testing](#testing)
- [Production Deployment](#production-deployment)
- [Examples](#examples)

## 🏗️ Architecture

### System Components

```
┌─────────────────┐
│   FastAPI       │ ← REST API Layer
│   Service      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Business      │ ← Core Logic Layer
│   Processor     │   (CaseSimilarityProcessor)
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│ Agent  │ │ Database │ ← Service Layer
│ Layer  │ │ Services │
└────────┘ └──────────┘
    │           │
    ▼           ▼
┌────────┐ ┌──────────┐
│  LLM   │ │  Qdrant  │ ← Infrastructure Layer
│ APIs   │ │ MongoDB  │
└────────┘ │  Redis   │
           └──────────┘
```

### Design Patterns

- **Strategy Pattern**: Different agent implementations share a common base
- **Singleton Pattern**: Database clients use singleton pattern for connection pooling
- **Factory Pattern**: Agent creation and initialization
- **Repository Pattern**: Data access abstraction through service layer

## 📁 Project Structure

```
multi-agents-boilerplate/
├── source/
│   ├── agents/                    # Agent implementations
│   │   ├── __init__.py           # Agent exports
│   │   ├── base.py               # BaseAgent abstract class
│   │   └── case_name_extractor/  # Example: Case naming agent
│   │       ├── __init__.py
│   │       ├── agent.py          # Agent implementation
│   │       └── prompt.py         # Prompts and instructions
│   │
│   ├── config/                    # Configuration management
│   │   └── __init__.py           # AppConfig with Pydantic BaseSettings
│   │
│   ├── db_clients/                # Database service clients
│   │   ├── __init__.py
│   │   ├── qdrant_scv.py         # Qdrant vector database
│   │   ├── mongo_svc.py          # MongoDB service
│   │   └── redis_svc.py          # Redis cache service
│   │
│   ├── models/                    # Data models
│   │   ├── __init__.py
│   │   └── api_models.py         # Pydantic models for API
│   │
│   ├── services/                  # API and service layer
│   │   ├── __init__.py
│   │   └── api.py                # FastAPI application
│   │
│   ├── tools/                     # Utility tools
│   │
│   ├── utils/                     # Utility functions
│   │   └── telemetry.py          # Logging and monitoring
│   │
│   ├── case_similarity.py         # Main processor logic
│   └── requirements.txt           # Python dependencies
│
│── tests/                     # Test suite
│   ├── conftest.py           # Pytest configuration
│   ├── test_agents.py        # Agent tests
│   ├── test_api.py           # API endpoint tests
│   ├── test_db_services.py   # Database tests
│   └── ...
├── .env                           # Environment variables
├── .gitignore                     # Git ignore rules
├── pytest.ini                     # Pytest configuration
└── README.md                      # This file
```

## 🧠 Core Concepts

### 1. Base Agent Class

All agents inherit from `BaseAgent`, which provides:

- **LLM Integration**: Pre-configured OpenAI-like model
- **Consistent Initialization**: Standard agent setup
- **Metadata Management**: Agent information tracking
- **Abstract Interface**: `run()` method must be implemented

```python
from source.agents.base import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="My Custom Agent",
            temperature=0.7,
            max_tokens=2000
        )
    
    async def run(self, *args, **kwargs) -> Dict[str, Any]:
        # Your agent logic here
        pass
```

### 2. Business Processor

The processor layer (`CaseSimilarityProcessor`) handles:

- **Data Processing**: Transform and validate input data
- **Agent Orchestration**: Coordinate multiple agents
- **Database Operations**: Interact with vector stores and databases
- **Business Logic**: Implement domain-specific rules

### 3. Database Services

Database clients follow singleton pattern:

```python
from source.db_clients.qdrant_scv import AsyncQdrantService

# Get singleton instance
qdrant_client = AsyncQdrantService()

# Use throughout your application
await qdrant_client.search(...)
```

### 4. Configuration Management

Centralized configuration using Pydantic:

```python
from source.config import settings

# Access configuration
qdrant_uri = settings.QDRANT_URI
llm_model = settings.LLM_MODEL_NAME
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Access to a Qdrant instance (or Docker)
- LLM API key (OpenAI, Claude, or compatible)
- (Optional) MongoDB and Redis instances

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd multi-agents-boilerplate
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Linux/Mac
   # or
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r source/requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Configure your environment**
   
   Edit `.env` file with your credentials:
   ```env
   # Qdrant Configuration
   QDRANT_URI=http://localhost
   QDRANT_PORT=6333
   QDRANT_API_KEY=your_api_key
   QDRANT_COLLECTION_NAME=your_collection
   
   # LLM Configuration
   OPENAI_API_KEY=your_openai_key
   OPENAI_MODEL_NAME=gpt-4o-mini
   OPENAI_API_BASE_URL=https://api.openai.com/v1
   
   # See .env for all options
   ```

### Quick Start

1. **Start the API server**
   ```bash
   cd source/services
   python api.py
   ```

2. **Access the API documentation**
   - API Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

3. **Make your first request**
   ```bash
   curl -X POST "http://localhost:8000/process-case" \
     -H "Content-Type: application/json" \
     -d @example_request.json
   ```

## 🔧 Creating Your Own Agent

### Step 1: Create Agent Directory

```bash
mkdir -p source/agents/my_agent
touch source/agents/my_agent/__init__.py
touch source/agents/my_agent/agent.py
touch source/agents/my_agent/prompt.py
```

### Step 2: Define Your Prompts

**File: `source/agents/my_agent/prompt.py`**

```python
PROMPTS = {}

PROMPTS['system_prompt'] = """
You are an expert AI agent that...

Your task is to...

Follow these rules:
1. ...
2. ...
"""

PROMPTS['user_prompt'] = """
Process the following input:
{input_data}
"""
```

### Step 3: Implement Your Agent

**File: `source/agents/my_agent/agent.py`**

```python
from textwrap import dedent
from pydantic import BaseModel, Field
from eb_labs.agent import Agent

from source.agents.base import BaseAgent
from source.agents.my_agent.prompt import PROMPTS

class MyAgentOutput(BaseModel):
    result: str = Field(..., description="The processed result")
    confidence: float = Field(..., description="Confidence score")

class MyCustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="My Custom Agent",
            temperature=0.3,
            max_tokens=1000,
            reasoning_effort='low'
        )
        
        self.agent = Agent(
            model=self.model,
            instructions=dedent(PROMPTS['system_prompt']),
            use_json_mode=True,
            debug_mode=True,
            output_schema=MyAgentOutput
        )
    
    async def run(self, input_data: str) -> dict:
        """
        Process input data and return structured output
        
        Args:
            input_data: Input text to process
            
        Returns:
            Dictionary with result and confidence
        """
        prompt = PROMPTS['user_prompt'].format(input_data=input_data)
        response = await self.agent.arun(prompt)
        
        return {
            "result": response.content.result,
            "confidence": response.content.confidence
        }
```

### Step 4: Export Your Agent

**File: `source/agents/__init__.py`**

```python
from source.agents.case_name_extractor.agent import CaseNamingAgent
from source.agents.my_agent.agent import MyCustomAgent  # Add this

__all__ = [
    'CaseNamingAgent',
    'MyCustomAgent',  # Add this
]
```

### Step 5: Use Your Agent

```python
from source.agents import MyCustomAgent

agent = MyCustomAgent()
result = await agent.run("Your input data here")
print(result)
```

## 🌐 API Usage

### Health Check

```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-20T10:30:00+07:00",
  "service": "Case Similarity Processing API"
}
```

### Process Case (Synchronous)

```bash
POST /process-case
```

**Request:**
```json
{
  "score_threshold": 0.85,
  "limit": 5,
  "radius_coordinate": 300.0,
  "report_type": "BOM",
  "data": {
    "input": "Your input text here",
    "created_at": "2025-10-20 10:30:00 +0700",
    "location_details": {
      "city_name": "JAKARTA",
      "coordinate": {
        "lat": -6.2088,
        "lon": 106.8456
      }
    }
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Case processed successfully",
  "case_id": "BOM-JKT-20251020-01-A4F5",
  "data_id": "unique-data-id",
  "similar_cases_count": 3,
  "is_new_case": false,
  "processing_time": 1.234,
  "case_name": "Generated Case Name"
}
```

### Process Case (Asynchronous)

```bash
POST /process-case-async
```

Returns immediately with a task ID for background processing.

### Find Similar Cases

```bash
GET /find-similar?text=your+search+text&coordinate_lat=-6.2088&coordinate_lon=106.8456
```

### Get Latest Report

```bash
POST /report/latest
```

**Request:**
```json
{
  "case_id": "BOM-JKT-20251020-01-A4F5",
  "start_time": "2025-10-01 00:00:00 +0700",
  "end_time": "2025-10-20 23:59:59 +0700",
  "limit": 10
}
```

## ⚙️ Configuration

### Environment Variables

The application uses Pydantic BaseSettings for configuration management. All settings are loaded from `.env` file:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `QDRANT_URI` | Qdrant server URL | Yes | - |
| `QDRANT_PORT` | Qdrant server port | Yes | - |
| `QDRANT_API_KEY` | Qdrant API key | Yes | - |
| `QDRANT_COLLECTION_NAME` | Collection name | Yes | - |
| `EMBEDDINGS_BASE_URL` | Embeddings service URL | Yes | - |
| `EMBEDDINGS_MODEL_NAME` | Embeddings model | Yes | - |
| `OPENAI_API_KEY` | OpenAI API key | Yes | - |
| `OPENAI_MODEL_NAME` | OpenAI model name | Yes | gpt-4o-mini |
| `OPENAI_API_BASE_URL` | OpenAI API URL | Yes | - |
| `LLM_TEMPERATURE` | LLM temperature | No | 0.1 |
| `LLM_MAX_TOKENS` | Maximum tokens | No | 8192 |
| `LLM_TIMEOUT` | Request timeout | No | 120 |
| `REDIS_HOST` | Redis host | No | - |
| `REDIS_PORT` | Redis port | No | - |
| `MONGO_DB_HOSTS` | MongoDB hosts | No | - |

### Adding Custom Configuration

1. **Update AppConfig class** in `source/config/__init__.py`:

```python
class AppConfig(BaseSettings):
    # ... existing settings ...
    
    MY_CUSTOM_SETTING: str
    MY_OPTIONAL_SETTING: Optional[int] = 100
```

2. **Add to `.env` file**:

```env
MY_CUSTOM_SETTING=value
MY_OPTIONAL_SETTING=200
```

3. **Use in your code**:

```python
from source.config import settings

value = settings.MY_CUSTOM_SETTING
```

## 🗄️ Database Services

### Qdrant Vector Database

**Synchronous Client:**
```python
from source.db_clients.qdrant_scv import QdrantService

client = QdrantService()
results = client.search(
    collection_name="my_collection",
    query_vector=[...],
    limit=10
)
```

**Asynchronous Client:**
```python
from source.db_clients.qdrant_scv import AsyncQdrantService

client = AsyncQdrantService()
results = await client.search(
    collection_name="my_collection",
    query_vector=[...],
    limit=10
)
```

### MongoDB (Optional)

```python
from source.db_clients.mongo_svc import MongoService

mongo = MongoService()
# Use mongo client
```

### Redis (Optional)

```python
from source.db_clients.redis_svc import RedisService

redis = RedisService()
# Use redis client
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_agents.py

# Run with coverage
pytest --cov=source tests/

# Run with verbose output
pytest -v tests/
```

### Test Structure

```
tests/
├── conftest.py              # Pytest fixtures and configuration
├── test_agents.py           # Agent unit tests
├── test_api.py              # API endpoint tests
├── test_db_services.py      # Database service tests
├── test_integration.py      # Integration tests
└── test_models.py           # Data model tests
```

### Writing Tests

**Example Test:**
```python
import pytest
from source.agents import MyCustomAgent

@pytest.mark.asyncio
async def test_my_agent():
    agent = MyCustomAgent()
    result = await agent.run("test input")
    
    assert result is not None
    assert "result" in result
    assert result["confidence"] > 0
```

## 🚀 Production Deployment

### Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY source/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY source/ ./source/
COPY .env .

EXPOSE 8000

CMD ["uvicorn", "source.services.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and Run:**
```bash
docker build -t multi-agent-api .
docker run -p 8000:8000 --env-file .env multi-agent-api
```

### Docker Compose

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - qdrant
      - redis
  
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
  
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

volumes:
  qdrant_data:
```

### Environment-Specific Configuration

```bash
# Development
export AGENT_STAGE=dev

# Staging
export AGENT_STAGE=staging

# Production
export AGENT_STAGE=prod
```

### Performance Tuning

1. **Adjust worker processes** (Gunicorn):
   ```bash
   gunicorn source.services.api:app \
     --workers 4 \
     --worker-class uvicorn.workers.UvicornWorker \
     --bind 0.0.0.0:8000
   ```

2. **Enable connection pooling** for databases

3. **Use async operations** wherever possible

4. **Implement caching** with Redis for frequent queries

## 💡 Examples

### Example 1: Creating a Sentiment Analysis Agent

```python
# source/agents/sentiment/agent.py
from source.agents.base import BaseAgent
from pydantic import BaseModel

class SentimentOutput(BaseModel):
    sentiment: str
    score: float

class SentimentAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_name="Sentiment Analysis Agent",
            temperature=0.2
        )
    
    async def run(self, text: str) -> dict:
        prompt = f"Analyze the sentiment of: {text}"
        # Your implementation here
        return {"sentiment": "positive", "score": 0.85}
```

### Example 2: Chaining Multiple Agents

```python
from source.agents import CaseNamingAgent, MyCustomAgent

async def process_with_multiple_agents(data):
    # First agent
    naming_agent = CaseNamingAgent()
    case_name = await naming_agent.run(data)
    
    # Second agent
    custom_agent = MyCustomAgent()
    analysis = await custom_agent.run(case_name)
    
    return {
        "case_name": case_name,
        "analysis": analysis
    }
```

### Example 3: Custom Business Processor

```python
class MyProcessor:
    def __init__(self):
        self.agent = MyCustomAgent()
        self.db = AsyncQdrantService()
    
    async def process(self, data: dict):
        # Process with agent
        result = await self.agent.run(data["input"])
        
        # Store in database
        await self.db.upsert(...)
        
        return result
```

## 🎓 Best Practices

1. **Agent Design**
   - Keep agents focused on single responsibilities
   - Use clear, descriptive system prompts
   - Define structured output schemas with Pydantic
   - Handle errors gracefully

2. **Code Organization**
   - Separate concerns (agents, services, models)
   - Use type hints throughout
   - Write comprehensive docstrings
   - Follow PEP 8 style guide

3. **Configuration**
   - Never hardcode credentials
   - Use environment variables
   - Validate configuration at startup
   - Document all settings

4. **Testing**
   - Write unit tests for agents
   - Test API endpoints
   - Mock external dependencies
   - Use fixtures for common test data

5. **Performance**
   - Use async/await for I/O operations
   - Implement connection pooling
   - Cache frequently accessed data
   - Monitor and profile your code

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure virtual environment is activated
   - Check `sys.path` configuration
   - Verify package installation

2. **Database Connection Issues**
   - Verify database is running
   - Check credentials in `.env`
   - Test network connectivity

3. **LLM API Errors**
   - Verify API key is correct
   - Check rate limits
   - Monitor token usage

4. **Agent Not Working**
   - Check system prompts
   - Verify output schema
   - Enable debug mode

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Python Async/Await Guide](https://docs.python.org/3/library/asyncio.html)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- eb_labs framework for agent orchestration
- Qdrant team for vector database
- FastAPI community
- OpenAI and Anthropic for LLM capabilities

---

**Note**: This is a boilerplate template. Customize it according to your specific use case and requirements. The example implementation (case similarity detection) can be replaced with your own business logic while keeping the overall architecture intact.

For questions or support, please open an issue on the repository.
