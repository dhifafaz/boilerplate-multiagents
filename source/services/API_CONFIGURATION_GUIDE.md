# API Configuration Guide

This guide explains how to configure, version, and document the Case Similarity Processing API.

## Table of Contents

- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Versioning](#versioning)
- [Documentation](#documentation)
- [Endpoint Tags](#endpoint-tags)
- [Production Deployment](#production-deployment)

## Quick Start

### Running the API

```bash
cd source/services
python api.py
```

The API will start on `http://0.0.0.0:8000` by default.

### Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## Configuration

All configuration is centralized in `source/config/api_config.py`. This makes it easy to update settings without modifying the main API code.

### Key Configuration Sections

#### 1. Version Configuration

```python
API_VERSION = "1.0.0"
API_PREFIX = "/api/v1"
```

**To upgrade to v2:**
```python
API_VERSION = "2.0.0"
API_PREFIX = "/api/v2"
```

#### 2. API Metadata

```python
API_TITLE = "Case Similarity Processing API"
API_DESCRIPTION = """Your API description here"""
```

Edit these to change the API title and main description shown in documentation.

#### 3. Contact Information

```python
CONTACT_INFO = {
    "name": "API Support Team",
    "email": "support@example.com",
    "url": "https://example.com/support"
}
```

#### 4. Tags Metadata

```python
TAGS_METADATA = [
    {
        "name": "Health",
        "description": "Health check endpoints",
        "externalDocs": {
            "description": "External documentation",
            "url": "https://example.com/docs/health"
        }
    },
    # ... more tags
]
```

Tags organize endpoints into logical groups in the documentation.

#### 5. CORS Configuration

```python
CORS_ORIGINS = ["*"]  # For development
# For production:
CORS_ORIGINS = [
    "https://yourdomain.com",
    "https://app.yourdomain.com",
]
```

#### 6. Server Configuration

```python
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000
SERVER_RELOAD = False  # Set True for development
```

#### 7. Default Parameters

```python
DEFAULT_SCORE_THRESHOLD = 0.0
DEFAULT_COORDINATE_RADIUS = 500.0  # meters
DEFAULT_RESULT_LIMIT = 10
```

## Versioning

### URL-Based Versioning

This API uses URL-based versioning, which is the most straightforward and widely adopted approach.

**Current endpoints:**
- `/api/v1/health`
- `/api/v1/process-case`
- `/api/v1/find-similar`
- etc.

### Creating a New Version

1. **Update `api_config.py`:**
   ```python
   API_VERSION = "2.0.0"
   API_PREFIX = "/api/v2"
   ```

2. **Maintain backward compatibility** by running multiple versions:
   ```python
   # In api.py, you can create multiple apps
   app_v1 = FastAPI(...)  # v1 endpoints
   app_v2 = FastAPI(...)  # v2 endpoints
   
   # Mount them
   main_app.mount("/api/v1", app_v1)
   main_app.mount("/api/v2", app_v2)
   ```

3. **Document breaking changes** in the API description

### Version Migration Strategy

**Recommended approach:**

1. **Minor updates (1.0.0 → 1.1.0)**: Add new features without breaking existing ones
2. **Major updates (1.x.x → 2.0.0)**: May include breaking changes
3. **Deprecation period**: Keep old versions running for 3-6 months
4. **Clear communication**: Update API description with migration guides

## Documentation

### Updating API Description

Edit the `API_DESCRIPTION` in `api_config.py`:

```python
API_DESCRIPTION = """
## Your API Name

Brief description here.

### Features

* Feature 1
* Feature 2

### Getting Started

Instructions here...

### Examples

Code examples here...
"""
```

The description supports **Markdown** formatting.

### Endpoint Documentation

Each endpoint has multiple documentation components:

```python
@app.post(
    f"{API_PREFIX}/endpoint",
    response_model=ResponseModel,
    tags=["Tag Name"],
    summary="Short summary",
    description="Detailed description",
    responses={
        200: {
            "description": "Success response",
            "content": {
                "application/json": {
                    "example": {
                        "key": "value"
                    }
                }
            }
        },
        404: {
            "description": "Not found",
        }
    }
)
async def endpoint_function():
    """
    Docstring appears in documentation.
    
    Use this for detailed explanation including:
    - Parameter descriptions
    - Return value details
    - Usage examples
    """
```

### Adding Examples

**In endpoint definition:**
```python
responses={
    200: {
        "content": {
            "application/json": {
                "example": {"status": "success"}
            }
        }
    }
}
```

**In Pydantic models:**
```python
class MyModel(BaseModel):
    field: str
    
    class Config:
        schema_extra = {
            "example": {
                "field": "example value"
            }
        }
```

## Endpoint Tags

Tags organize endpoints into logical groups in the documentation.

### Current Tags

1. **Health**: Service health checks
2. **Case Processing**: Case processing operations
3. **Search**: Search and similarity operations
4. **Reports**: Report management
5. **Information**: General API information

### Adding a New Tag

1. **Add to `TAGS_METADATA` in `api_config.py`:**
   ```python
   {
       "name": "New Category",
       "description": "Description of this category",
       "externalDocs": {
           "description": "External docs",
           "url": "https://example.com/docs"
       }
   }
   ```

2. **Use in endpoint:**
   ```python
   @app.get(
       f"{API_PREFIX}/new-endpoint",
       tags=["New Category"],
       # ... other parameters
   )
   ```

### Tag Best Practices

- Keep tags focused and clear
- Use 3-7 tags maximum
- Order tags by importance/frequency of use
- Provide detailed descriptions for each tag
- Link to external documentation when available

## Production Deployment

### Environment Variables

Override configuration using environment variables:

```bash
export API_VERSION="1.0.0"
export API_PREFIX="/api/v1"
export SERVER_HOST="0.0.0.0"
export SERVER_PORT="8000"
export LOG_LEVEL="INFO"
```

### Production Checklist

- [ ] Update CORS origins to specific domains
- [ ] Set `SERVER_RELOAD = False`
- [ ] Configure proper logging
- [ ] Set up API authentication (when implemented)
- [ ] Enable rate limiting (when implemented)
- [ ] Update contact information
- [ ] Review and update API description
- [ ] Test all endpoints
- [ ] Document breaking changes
- [ ] Set up monitoring and alerts

### Security Considerations

1. **CORS**: Specify exact origins, don't use `["*"]`
2. **Authentication**: Implement API keys or OAuth2
3. **Rate Limiting**: Prevent abuse
4. **Input Validation**: All inputs are validated via Pydantic
5. **Error Messages**: Don't expose sensitive information

### Performance Optimization

1. **Background Tasks**: Use for long-running operations
2. **Caching**: Implement Redis caching for frequent queries
3. **Database Indexing**: Ensure proper indexes on Qdrant
4. **Connection Pooling**: Configure appropriate pool sizes
5. **Async Operations**: All endpoints use async/await

### Monitoring

Add these to your deployment:

1. **Health Checks**: Use `/api/v1/health` endpoint
2. **Metrics**: Track response times, error rates
3. **Logging**: Configure structured logging
4. **Alerting**: Set up alerts for errors and slow responses

### Docker Deployment

Example `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV SERVER_HOST=0.0.0.0
ENV SERVER_PORT=8000
ENV LOG_LEVEL=INFO

EXPOSE 8000

CMD ["python", "source/services/api.py"]
```

Example `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - API_VERSION=1.0.0
      - API_PREFIX=/api/v1
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
```

## Advanced Configuration

### Multiple Environment Support

Create environment-specific config files:

```python
# config/api_config_dev.py
from .api_config import *

SERVER_RELOAD = True
LOG_LEVEL = "DEBUG"
CORS_ORIGINS = ["*"]
```

```python
# config/api_config_prod.py
from .api_config import *

SERVER_RELOAD = False
LOG_LEVEL = "WARNING"
CORS_ORIGINS = ["https://yourdomain.com"]
```

Load based on environment:

```python
import os
env = os.getenv("ENV", "dev")

if env == "production":
    from source.config.api_config_prod import *
else:
    from source.config.api_config_dev import *
```

### Feature Flags

Control features via configuration:

```python
FEATURES = {
    "async_processing": True,
    "authentication": False,
    "rate_limiting": False,
}

# In api.py
if FEATURES["async_processing"]:
    @app.post(f"{API_PREFIX}/process-case-async")
    async def process_case_async(...):
        ...
```

## Support

For questions or issues with configuration:

- Check the [FastAPI documentation](https://fastapi.tiangolo.com/)
- Review the configuration file: `source/config/api_config.py`
- Contact the development team

## Changelog

### v1.0.0 (2025-10-24)
- Initial release with versioning support
- Comprehensive documentation
- Tag-based endpoint organization
- Centralized configuration
