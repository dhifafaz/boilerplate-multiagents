# Intel Report Case Similarity Detection System

A Agentic-based system for detecting and managing similar incident reports using vector embeddings and semantic search. The system automatically identifies related cases, generates case names, and maintains a knowledge base of incidents using Qdrant vector database.

## 🎯 Features

- **Semantic Similarity Search**: Find similar incident reports using vector embeddings (EBBGE-v2 model)
- **Automatic Case Clustering**: Group similar reports into cases with unique case IDs
- **AI-Powered Case Naming**: Generate descriptive case names using GPT-4o-mini
- **Location-Based Filtering**: Search by coordinates, districts, cities, and provinces
- **Time-Based Filtering**: Filter reports by timestamp ranges
- **Multi-Level Geospatial Search**: Search at coordinate, subdistrict, district, city, and province levels
- **RESTful API**: FastAPI-based API with automatic documentation
- **Asynchronous Processing**: Support for both sync and async processing
- **Comprehensive Reporting**: Track and retrieve reports by case ID

## 📋 Table of Contents

- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Data Models](#data-models)
- [Examples](#examples)
- [Development](#development)

## 🏗️ Architecture

### Components

1. **FastAPI Service** (`src/services/api.py`)
   - RESTful API endpoints
   - Request/response handling
   - CORS middleware
   - Error handling

2. **Case Similarity Processor** (`src/case_similarity.py`)
   - Core similarity detection logic
   - Qdrant vector database integration
   - Case ID generation
   - Location data processing

3. **Case Naming Agent** (`src/agents/case_name.py`)
   - AI-powered case name generation
   - Uses GPT-4o-mini via eb_labs framework
   - Generates concise, descriptive names in Bahasa Indonesia

4. **Database Services** (`src/db_service/`)
   - Qdrant vector database client
   - MongoDB service (optional)
   - Redis service (optional)

5. **Data Models** (`src/models/api_models.py`)
   - Pydantic models for request/response validation
   - Type safety and data validation

### Technology Stack

- **Framework**: FastAPI
- **Vector Database**: Qdrant
- **Embeddings**: EBBGE-v2 (via langchain-ebdesk)
- **AI Agent**: eb_labs + OpenAI GPT-4o-mini
- **Async Runtime**: asyncio, httpx
- **Validation**: Pydantic

## 🚀 Installation

### Prerequisites

- Python 3.8+
- Access to internal PyPI server (192.168.20.26:6060)
- Qdrant vector database instance
- OpenAI API key (or compatible LLM endpoint)

### Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bomb-case-similarity
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
   pip install -r src/requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## ⚙️ Configuration

Create a `.env` file in the project root with the following variables:

```env
# Qdrant Configuration
QDRANT_URI=http://10.12.1.110
QDRANT_PORT=6300
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION_NAME=test_bomb_case_similarity_ebbge_v2

# Embeddings Configuration
EMBEDDINGS_BASE_URL=http://10.12.120.32:7653
EMBEDDINGS_MODEL_NAME=ebbge-v2

# LLM Configuration
LLM_BASE_URL=http://10.12.120.42:8787/v1
LLM_API_KEY=your_llm_api_key
LLM_MODEL_NAME=Qwen3-8B
LLM_PROVIDER=ebdesk

# OpenAI Configuration (for case naming)
OPENAI_API_KEY=your_openai_api_key

# Agent Configuration
AGENT_STAGE=test
AGENT_NAME=BombCaseSimilarityAgent

# Clustering Configuration (optional)
CLUSTERING_BASE_URL=http://10.12.120.32:7777
CLUSTERING_RELEVANCE=80
CLUSTERING_MODEL_NAME=ebbge-v2
CLUSTERING_METRIC=cosine
CLUSTERING_N_CLUSTERS=25
```

## 📘 Usage

### Starting the API Server

```bash
cd src/services
python api.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Running as Module

```bash
python -m uvicorn source.services.api:app --host 0.0.0.0 --port 8000 --reload
```

## 🌐 API Endpoints

### 1. Health Check

**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-20T10:30:00+07:00",
  "service": "Case Similarity Processing API"
}
```

### 2. Process Case (Synchronous)

**POST** `/process-case`

Process a case report and find similar cases.

**Request Body:**
```json
{
  "score_threshold": 0.85,
  "limit": 5,
  "radius_coordinate": 300.0,
  "report_type": "BOM",
  "data": {
    "input": "Ada ledakan di dekat gedung XYZ",
    "created_at": "2025-10-20 10:30:00 +0700",
    "location_details": {
      "district_name": "PONDOK AREN",
      "city_name": "KOTA TANGERANG SELATAN",
      "subdistrict_name": "PARIGI BARU",
      "coordinate": {
        "lat": -6.2680494,
        "lon": 106.68715499999999
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
  "case_id": "BOM-TSL-20251020-01-A4F5",
  "data_id": "unique-data-id",
  "similar_cases_count": 3,
  "score_threshold": 0.85,
  "radius_coordinate": 300.0,
  "is_new_case": false,
  "processing_time": 1.234,
  "case_name": "Ledakan di Gedung XYZ (Tangerang Selatan)"
}
```

### 3. Process Case (Asynchronous)

**POST** `/process-case-async`

Process a case in the background.

**Response:**
```json
{
  "status": "accepted",
  "message": "Case processing started in background",
  "task_id": "task_20251020_103000",
  "radius_coordinate": 300.0,
  "score_threshold": 0.85
}
```

### 4. Find Similar Cases

**GET** `/find-similar`

Find similar cases based on text and filters.

**Query Parameters:**
- `text` (required): Text to search for
- `coordinate_lat`: Latitude
- `coordinate_lon`: Longitude
- `timestamp`: Unix timestamp
- `subdistrict_code`: Subdistrict code
- `coordinate_max_radius`: Maximum search radius (default: 500m)
- `score_threshold`: Minimum similarity score (default: 0.0)
- `limit`: Maximum results (default: 10)

**Response:**
```json
[
  {
    "similarity_score": 0.92,
    "payload": {...},
    "metadata": {...}
  }
]
```

### 5. Get Latest Report

**POST** `/report/latest`

Get the most recent report for a specific case ID.

**Request Body:**
```json
{
  "case_id": "BOM-TSL-20251020-01-A4F5",
  "start_time": "2025-10-01 00:00:00 +0700",
  "end_time": "2025-10-20 23:59:59 +0700",
  "limit": 10
}
```

**Response:**
```json
{
  "status": "success",
  "case_id": "BOM-TSL-20251020-01-A4F5",
  "reports_found": 5,
  "latest_report": {
    "id": "report-id",
    "case_id": "BOM-TSL-20251020-01-A4F5",
    "report_text": "...",
    "created_at": "2025-10-20 10:30:00 +0700",
    "processed_at": "2025-10-20 10:30:05 +0700",
    "metadata": {...}
  },
  "query_time_range": {
    "start_time": "2025-10-01 00:00:00 +0700",
    "end_time": "2025-10-20 23:59:59 +0700"
  }
}
```

## 📊 Data Models

### InputDataModel

The main input model for processing cases:

```python
{
  "score_threshold": float,  # Similarity threshold (0.0-1.0)
  "limit": int,              # Max similar cases to find
  "radius_coordinate": float, # Search radius in meters
  "report_type": str,        # Type of report (e.g., "BOM")
  "data": {
    "input": str,            # Report text
    "created_at": str,       # Format: "YYYY-MM-DD HH:MM:SS +ZZZZ"
    "location_details": {
      "district_name": str,
      "city_name": str,
      "coordinate": {
        "lat": float,
        "lon": float
      },
      # ... more location fields
    },
    # Optional fields
    "sketch": str,           # Sketch URL
    "images": List[dict],    # Image URLs
    "raw_message": str,      # Original message
    "first_name": str,       # Reporter name
    "username": str          # Reporter username
  }
}
```

### Case ID Format

Case IDs follow this pattern:
```
{CATEGORY}-{LOCATION_CODE}-{DATE}-{DAILY_INDEX}-{HASH}
```

Example: `BOM-TSL-20251020-01-A4F5`

- **CATEGORY**: Report type (BOM, DEMO, FIRE, etc.)
- **LOCATION_CODE**: Location abbreviation
- **DATE**: YYYYMMDD format
- **DAILY_INDEX**: Sequential number for the day
- **HASH**: 4-character hash for uniqueness

## 💡 Examples

### Python Client Example

```python
import httpx
import asyncio

async def process_case():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/process-case",
            json={
                "score_threshold": 0.85,
                "limit": 5,
                "radius_coordinate": 300.0,
                "report_type": "BOM",
                "data": {
                    "input": "Ledakan di gedung ABC",
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
        )
        print(response.json())

asyncio.run(process_case())
```

### cURL Example

```bash
curl -X POST "http://localhost:8000/process-case" \
  -H "Content-Type: application/json" \
  -d '{
    "score_threshold": 0.85,
    "limit": 5,
    "radius_coordinate": 300.0,
    "report_type": "BOM",
    "data": {
      "input": "Ledakan di gedung ABC",
      "created_at": "2025-10-20 10:30:00 +0700",
      "location_details": {
        "city_name": "JAKARTA",
        "coordinate": {
          "lat": -6.2088,
          "lon": 106.8456
        }
      }
    }
  }'
```

## 🛠️ Development

### Project Structure

```
bomb-case-similarity/
├── README.md
├── .env
├── src/
│   ├── case_similarity.py       # Core processor
│   ├── requirements.txt
│   ├── agents/
│   │   ├── __init__.py
│   │   └── case_name.py        # Case naming agent
│   ├── config/
│   │   └── __init__.py         # Configuration
│   ├── db_service/
│   │   ├── __init__.py
│   │   ├── qdrant_scv.py       # Qdrant service
│   │   ├── mongo_svc.py        # MongoDB service
│   │   └── redis_svc.py        # Redis service
│   ├── models/
│   │   ├── __init__.py
│   │   └── api_models.py       # Pydantic models
│   └── services/
│       ├── __init__.py
│       └── api.py              # FastAPI application
└── archive/                     # Old versions
```

### Running Tests

```bash
# Run with pytest (if tests are available)
pytest tests/
```

### Code Style

The project uses:
- Python 3.8+ type hints
- Pydantic for data validation
- Async/await for I/O operations
- Loguru for logging

## 🔍 How It Works

### 1. Case Processing Flow

```
Input Report
    ↓
Extract Location Data
    ↓
Normalize Coordinates
    ↓
Create Qdrant Filters
    ↓
Search Similar Cases (Vector Search)
    ↓
├─ Similar Cases Found?
│  ├─ Yes → Link to Existing Case
│  └─ No → Generate New Case ID & Name
    ↓
Store in Qdrant
    ↓
Return Response
```

### 2. Similarity Detection

The system uses:
- **Vector Embeddings**: EBBGE-v2 model converts text to vectors
- **Semantic Search**: Qdrant finds similar vectors
- **Multi-Level Filtering**:
  - Coordinate-based (radius search)
  - Administrative boundaries (subdistrict, district, city, province)
  - Temporal filtering (timestamp ranges)
- **Score Threshold**: Configurable minimum similarity score

### 3. Case ID Generation

Case IDs are generated using:
- Report category
- Location code (extracted from administrative data)
- Date
- Daily sequential index
- SHA256 hash (4 chars) for uniqueness

## 📝 License

[Add your license information here]

## 👥 Contributors

[Add contributor information here]

## 📧 Contact

For questions or support, please contact [your contact information]

## 🔗 Related Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [eb_labs Framework]() (internal)
