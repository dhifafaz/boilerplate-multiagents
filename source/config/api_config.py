"""
API Configuration File

This file contains all configuration settings for the API.
Modify these values to easily update the API without changing the main code.
"""

# ========================================
# Version Configuration
# ========================================
API_VERSION = "1.0.0"
API_PREFIX = "/api/v1"

# To upgrade to v2, simply change:
# API_VERSION = "2.0.0"
# API_PREFIX = "/api/v2"

# ========================================
# API Metadata
# ========================================
API_TITLE = "Case Similarity Processing API"
API_DESCRIPTION = """
## Case Similarity Processing API

This API provides comprehensive case similarity analysis using vector embeddings and location-based filtering.

### Features

* **Case Processing**: Process and analyze case data with similarity detection
* **Similar Case Search**: Find similar cases based on text, location, and temporal filters
* **Report Management**: Retrieve and manage case reports with time-based filtering
* **Background Processing**: Asynchronous processing for large datasets

### Key Capabilities

#### 1. Semantic Search
Uses advanced vector embeddings to find semantically similar cases, even when exact word matches don't exist.

#### 2. Multi-Dimensional Filtering
Combine multiple filters:
- Text similarity scores
- Geographic proximity (coordinate-based)
- Temporal filtering (timestamp-based)
- Administrative regions (subdistrict codes)

#### 3. Scalable Processing
- Synchronous processing for immediate results
- Asynchronous processing for large batches
- Configurable thresholds and limits

### Authentication

Currently, no authentication is required. Future versions will include:
- API Key authentication
- OAuth2 support
- Role-based access control (RBAC)

### Rate Limiting

No rate limiting is currently enforced. Please use responsibly.

**Recommended limits:**
- 100 requests per minute per IP
- 1000 requests per hour per API key

### Versioning

This API uses URL-based versioning. The current version is `v1`.

**Version History:**
- **v1.0.0** (Current): Initial release with core functionality

### Support

For support, questions, or bug reports:
- Email: support@example.com
- Documentation: See `/docs` for interactive API documentation

### Response Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 404  | Resource not found |
| 422  | Validation error |
| 500  | Internal server error |
"""

# ========================================
# Contact Information
# ========================================
CONTACT_INFO = {
    "name": "API Support Team",
    "email": "support@example.com",
    "url": "https://example.com/support"
}

# ========================================
# License Information
# ========================================
LICENSE_INFO = {
    "name": "MIT License",
    "url": "https://opensource.org/licenses/MIT"
}

# ========================================
# Tags Metadata for Endpoint Grouping
# ========================================
TAGS_METADATA = [
    {
        "name": "Health",
        "description": "Health check and service status endpoints. Use these to monitor API availability and status.",
        "externalDocs": {
            "description": "Health check best practices",
            "url": "https://example.com/docs/health-checks"
        }
    },
    {
        "name": "Case Processing",
        "description": """
        Operations for processing and analyzing case data.
        
        **Synchronous Processing**: Use `/process-case` when you need immediate results.
        
        **Asynchronous Processing**: Use `/process-case-async` for large batches or when you can 
        tolerate delays. Returns a task ID for tracking.
        
        **Use Cases:**
        - Creating new cases
        - Finding similar existing cases
        - Updating case information
        - Batch processing of multiple cases
        """,
        "externalDocs": {
            "description": "Case processing guide",
            "url": "https://example.com/docs/case-processing"
        }
    },
    {
        "name": "Search",
        "description": """
        Search operations for finding similar cases based on various criteria.
        
        **Search Methods:**
        - Text-based semantic similarity
        - Location-based proximity search
        - Time-based filtering
        - Administrative region filtering
        
        **Advanced Features:**
        - Configurable similarity thresholds
        - Multi-filter combinations
        - Result limiting and pagination
        """,
        "externalDocs": {
            "description": "Search API guide",
            "url": "https://example.com/docs/search-api"
        }
    },
    {
        "name": "Reports",
        "description": """
        Report management and retrieval operations.
        
        **Features:**
        - Get latest reports by case ID
        - Time-range filtering
        - Full metadata access
        - Sorted results (most recent first)
        
        **Time Format:**
        All timestamps use format: `YYYY-MM-DD HH:MM:SS +ZZZZ`
        
        Example: `2025-10-24 10:00:00 +0700`
        """,
        "externalDocs": {
            "description": "Reports documentation",
            "url": "https://example.com/docs/reports"
        }
    },
    {
        "name": "Information",
        "description": """
        General API information and documentation.
        
        Access API metadata, available endpoints, versioning information, and links to documentation.
        """,
    },
]

# ========================================
# CORS Configuration
# ========================================
CORS_ORIGINS = ["*"]  # In production, specify exact origins
CORS_CREDENTIALS = True
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"]

# For production, use specific origins:
# CORS_ORIGINS = [
#     "https://yourdomain.com",
#     "https://app.yourdomain.com",
# ]

# ========================================
# Server Configuration
# ========================================
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000
SERVER_RELOAD = False  # Set to True for development
SERVER_WORKERS = 4  # Number of worker processes

# ========================================
# Default Query Parameters
# ========================================
DEFAULT_SCORE_THRESHOLD = 0.0
DEFAULT_COORDINATE_RADIUS = 500.0  # meters
DEFAULT_RESULT_LIMIT = 10
DEFAULT_REPORT_LIMIT = 10

# ========================================
# Logging Configuration
# ========================================
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ========================================
# Timezone Configuration
# ========================================
TIMEZONE = "Asia/Jakarta"

# ========================================
# Documentation URLs
# ========================================
DOCS_URL = "/docs"
REDOC_URL = "/redoc"
OPENAPI_URL_TEMPLATE = "{api_prefix}/openapi.json"

def get_openapi_url():
    """Generate OpenAPI URL based on current API prefix"""
    return OPENAPI_URL_TEMPLATE.format(api_prefix=API_PREFIX)

# ========================================
# Feature Flags
# ========================================
FEATURES = {
    "async_processing": True,
    "background_tasks": True,
    "location_filtering": True,
    "time_filtering": True,
    "authentication": False,  # Not yet implemented
    "rate_limiting": False,   # Not yet implemented
}

# ========================================
# Environment-Specific Configuration
# ========================================
# You can override these in production using environment variables

import os

# Override from environment variables
API_VERSION = os.getenv("API_VERSION", API_VERSION)
API_PREFIX = os.getenv("API_PREFIX", API_PREFIX)
SERVER_HOST = os.getenv("SERVER_HOST", SERVER_HOST)
SERVER_PORT = int(os.getenv("SERVER_PORT", SERVER_PORT))
LOG_LEVEL = os.getenv("LOG_LEVEL", LOG_LEVEL)
