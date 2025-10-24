# Test Suite Documentation

This directory contains the comprehensive test suite for the **Case Similarity Processing System** - a system that processes case reports, generates case IDs, finds similar cases using vector search, and manages case data across multiple databases.

## Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_api.py              # FastAPI endpoint tests (9 test cases)
├── test_case_similarity.py  # Core processor logic tests (13 test cases)
├── test_models.py           # Pydantic model tests (15 test cases)
├── test_agents.py           # AI agent tests (5 test cases)
├── test_db_services.py      # Database service tests (8 test cases)
├── test_utils.py            # Utility function tests (8 test cases)
├── test_integration.py      # Integration tests (3 test cases)
└── README.md                # This file
```

**Total: 61 test cases** covering unit, integration, and API testing.

## Running Tests

### Run all tests
```bash
pytest source/tests/
```

### Run specific test file
```bash
pytest source/tests/test_api.py
```

### Run specific test class
```bash
pytest source/tests/test_api.py::TestAPIEndpoints
```

### Run specific test
```bash
pytest source/tests/test_api.py::TestAPIEndpoints::test_health_check
```

### Run tests with coverage
```bash
pytest source/tests/ --cov=source --cov-report=html
```

### Run only unit tests (skip integration)
```bash
pytest source/tests/ -m unit
```

### Run only integration tests
```bash
pytest source/tests/ -m integration
```

## Test Categories

### 1. Core Processor Tests (`test_case_similarity.py`) - 13 Tests
Tests for the main `CaseSimilarityProcessor` class that handles case processing logic:
- ✅ `test_generate_case_id` - Validates case ID format: `BOM-TSL-202510-01-ABCD`
- ✅ `test_normalize_coordinate` - Handles both `lon` and `long` coordinate fields
- ✅ `test_extract_location_data` - Extracts subdistrict, district, city, province codes
- ✅ `test_create_qdrant_filter` - Creates filters for vector search (coordinate, timestamp, location)
- ✅ `test_format_report` - Formats case data into readable report string
- ✅ `test_generate_case_name` - Generates human-readable case names using AI agent
- ✅ `test_find_similar_data` - Searches for similar cases using vector embeddings
- ✅ `test_insert_to_qdrant` - Inserts case data into Qdrant vector database
- ✅ `test_process_data_new_case` - Processes new case when no similar cases exist
- ✅ `test_process_data_existing_case` - Links to existing case when similar cases found
- ✅ `test_get_reports_by_case_id` - Retrieves all reports for a specific case ID

### 2. API Endpoint Tests (`test_api.py`) - 9 Tests
Tests for FastAPI REST endpoints:
- ✅ `test_health_check` - GET `/health` returns service status
- ✅ `test_root_endpoint` - GET `/` returns API documentation
- ✅ `test_process_case_success` - POST `/process-case` processes case successfully
- ✅ `test_process_case_invalid_data` - Validates input data and returns 422 error
- ✅ `test_process_case_async` - POST `/process-case-async` queues case for processing
- ✅ `test_find_similar_cases` - GET `/find-similar` searches for similar cases
- ✅ `test_get_latest_report` - POST `/report/latest` retrieves latest case reports
- ✅ `test_get_latest_report_not_found` - Returns 404 when no reports exist

### 3. Data Model Tests (`test_models.py`) - 15 Tests
Tests for Pydantic validation models:
- ✅ `test_coordinate_with_lon` - CoordinateModel accepts `lon` field
- ✅ `test_coordinate_with_long` - CoordinateModel accepts `long` field (maps to `lon`)
- ✅ `test_coordinate_optional_fields` - Handles optional coordinate fields
- ✅ `test_valid_case_data` - Validates complete CaseDataModel structure
- ✅ `test_invalid_created_at_format` - Rejects invalid datetime format
- ✅ `test_optional_fields` - Validates optional fields (sketch, images, audios, etc.)
- ✅ `test_valid_input_data` - InputDataModel with all parameters
- ✅ `test_default_values` - Tests default values (score_threshold=0.85, limit=5, etc.)
- ✅ `test_success_response` - ProcessingResponseModel for successful processing
- ✅ `test_error_response` - ProcessingResponseModel for error cases
- ✅ `test_valid_report` - ReportModel structure validation
- ✅ `test_valid_request` - GetLatestReportRequest validation
- ✅ `test_default_limit` - Default limit value for report requests
- ✅ `test_valid_response` - LatestReportResponse structure

### 4. AI Agent Tests (`test_agents.py`) - 5 Tests
Tests for AI-powered agents:
- ✅ `test_run_success` - CaseNamingAgent generates case names from reports
- ✅ `test_run_with_different_reports` - Tests different report types (BOM, DEMO, FIRE)
- ✅ `test_base_agent_is_abstract` - BaseAgent cannot be instantiated directly
- ✅ `test_base_agent_subclass` - Valid BaseAgent subclass creation
- ✅ `test_get_metadata` - Retrieves agent metadata (model, temperature, tokens)

### 5. Database Service Tests (`test_db_services.py`) - 8 Tests
Tests for database service classes:
- ✅ `test_async_qdrant_service_singleton` - AsyncQdrantService singleton pattern
- ✅ `test_qdrant_service_singleton` - QdrantService singleton pattern
- ✅ `test_redis_service_singleton` - RedisService singleton pattern
- ✅ `test_mongo_singleton` - StellarConfigDB singleton pattern
- ✅ `test_get_all_collections` - MongoDB list all collections
- ✅ `test_get_by_id` - MongoDB retrieve document by ID
- ✅ `test_create_by_id` - MongoDB create new document
- ✅ `test_update_by_id` - MongoDB update existing document
- ✅ `test_delete_by_id` - MongoDB delete document

### 6. Utility Function Tests (`test_utils.py`) - 8 Tests
Tests for utility decorators and helpers:
- ✅ `test_sync_function_logging` - Logging decorator on sync functions
- ✅ `test_async_function_logging` - Logging decorator on async functions
- ✅ `test_sync_function_error_logging` - Error handling in sync functions
- ✅ `test_async_function_error_logging` - Error handling in async functions
- ✅ `test_class_method_logging` - Logging decorator on class methods
- ✅ `test_async_class_method_logging` - Logging decorator on async class methods
- ✅ `test_execution_time_logging` - Execution time tracking

### 7. Integration Tests (`test_integration.py`) - 3 Tests
End-to-end workflow tests:
- ✅ `test_complete_case_processing_workflow` - Full API to database workflow (skipped in CI)
- ✅ `test_similarity_detection_workflow` - Multiple report similarity detection (skipped in CI)
- ✅ `test_end_to_end_with_mocks` - Complete workflow with mocked services

## Test Fixtures

Common fixtures are defined in `conftest.py` for reuse across all test files:

### Data Fixtures
- **`sample_location_details`**: Complete location data with district, city, province codes and coordinates
- **`sample_case_data`**: Full case report with input, location, images, timestamp
- **`sample_input_data_model`**: API request model with score threshold, limits, report type

### Service Mocks
- **`mock_qdrant_client`**: Mocked AsyncQdrantClient for vector database operations
  - Methods: `search()`, `upsert()`, `scroll()`
- **`mock_embeddings`**: Mocked embeddings service for text vectorization
  - Methods: `aembed_query()` returns 768-dimensional vectors
- **`mock_case_naming_agent`**: Mocked AI agent for case name generation
  - Methods: `run()` returns generated case names
- **`mock_redis`**: Mocked Redis client for caching
  - Methods: `get()`, `set()`, `delete()`
- **`mock_mongo`**: Mocked MongoDB client for document storage
  - Methods: `get_by_id()`, `create_by_id()`, `update_by_id()`, `delete_by_id()`

### Async Testing
- **`event_loop`**: Session-scoped event loop for async test execution

## Test Markers

Tests are marked with custom markers:

- `@pytest.mark.unit`: Unit tests (default)
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.slow`: Slow running tests
- `@pytest.mark.asyncio`: Async tests

## Coverage Goals

**Target coverage: 80%+** for all modules

### Current Coverage Areas:
- ✅ **API endpoints** (`services/api.py`) - All endpoints tested
- ✅ **Core processor logic** (`case_similarity.py`) - All public methods tested
- ✅ **Data models** (`models/api_models.py`) - All models and validations tested
- ✅ **AI Agents** (`agents/`) - Agent initialization and execution tested
- ✅ **Database services** (`db/`) - Singleton patterns and CRUD operations tested
- ✅ **Utility functions** (`utils/telemetry.py`) - Logging decorator fully tested

### To check current coverage:
```bash
pytest source/tests/ --cov=source --cov-report=term-missing
```

### To generate HTML coverage report:
```bash
pytest source/tests/ --cov=source --cov-report=html
# Open htmlcov/index.html in browser
```

## Mocking Strategy

We use mocks to isolate unit tests and avoid external dependencies:

### What We Mock:
1. **Vector Database (Qdrant)**
   - AsyncQdrantClient for vector search operations
   - Mock responses for search, upsert, scroll operations

2. **AI Services**
   - OpenAI/LLM models for case naming
   - Embeddings service for text vectorization
   - Returns predefined 768-dimensional vectors

3. **Databases**
   - Redis for caching operations
   - MongoDB for document storage and retrieval

4. **Network & External APIs**
   - HTTP requests
   - External service calls

5. **Time-sensitive Operations**
   - datetime.now() for consistent timestamps
   - asyncio.sleep() for faster test execution

### Why We Mock:
- ✅ **Speed**: Tests run in milliseconds instead of seconds
- ✅ **Reliability**: No dependency on external services
- ✅ **Isolation**: Test one component at a time
- ✅ **Cost**: No API calls to paid services
- ✅ **CI/CD**: Tests run anywhere without setup

## Best Practices

1. **Isolation**: Each test should be independent
2. **Clarity**: Test names should describe what they test
3. **Coverage**: Aim for high code coverage
4. **Speed**: Unit tests should be fast
5. **Reliability**: Tests should be deterministic
6. **Maintainability**: Use fixtures for common setups

## Common Issues & Solutions

### Issue: Async tests not running
**Solution**: Install `pytest-asyncio` and use `@pytest.mark.asyncio` decorator
```python
@pytest.mark.asyncio
async def test_my_async_function():
    result = await my_async_function()
    assert result is not None
```

### Issue: Import errors
**Solution**: Ensure PYTHONPATH includes project root
```bash
export PYTHONPATH="${PYTHONPATH}:/home/dhifaf/multi-agents-boilerplate"
# Or run from project root
cd /home/dhifaf/multi-agents-boilerplate
pytest source/tests/
```

### Issue: Fixture not found
**Solution**: Check `conftest.py` is in the correct location and fixture name is correct
```python
# conftest.py must be in tests/ directory
# Use fixtures by name in test parameters
def test_something(sample_case_data):  # Fixture injected automatically
    pass
```

### Issue: Singleton conflicts between tests
**Solution**: Reset singleton instances in test setup or fixtures
```python
@pytest.fixture
def clean_singleton():
    # Reset before test
    ServiceClass.instance = None
    ServiceClass._is_initialized = False
    yield
    # Cleanup after test
    ServiceClass.instance = None
```

### Issue: Tests pass individually but fail when run together
**Solution**: Tests are not properly isolated. Check for:
- Shared state between tests
- Global variables being modified
- Singleton instances not being reset
- Database/cache not being cleaned up

### Issue: Mock not being applied
**Solution**: Patch at the correct location (where it's used, not where it's defined)
```python
# Correct: Patch where CaseNamingAgent is used
@patch('source.case_similarity.CaseNamingAgent')
def test_processor(mock_agent):
    processor = CaseSimilarityProcessor()  # Uses mocked agent
```

## Dependencies

### Required Testing Packages:
```
pytest>=7.4.0           # Core testing framework
pytest-asyncio>=0.21.0  # Async test support
pytest-cov>=4.1.0       # Coverage reporting
pytest-mock>=3.11.0     # Enhanced mocking capabilities
httpx>=0.27.0          # Async HTTP client for API testing
```

### Installation:
```bash
# Install from requirements-test.txt
pip install -r source/tests/requirements-test.txt

# Or install individually
pip install pytest pytest-asyncio pytest-cov pytest-mock httpx

# For development
pip install -r source/requirements.txt
```

### Verify Installation:
```bash
pytest --version
python -c "import pytest_asyncio; print('pytest-asyncio installed')"
```

## CI/CD Integration

### GitHub Actions Example:
```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r source/requirements.txt
        pip install -r source/tests/requirements-test.txt
    
    - name: Run unit tests with coverage
      run: |
        pytest source/tests/ \
          --cov=source \
          --cov-report=xml \
          --cov-report=term-missing \
          -m "not integration" \
          -v
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
```

### GitLab CI Example:
```yaml
test:
  stage: test
  image: python:3.10
  script:
    - pip install -r source/requirements.txt
    - pip install -r source/tests/requirements-test.txt
    - pytest source/tests/ --cov=source --cov-report=term --cov-report=html
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

## Test Statistics

- **Total Test Cases**: 61
- **Test Files**: 8
- **Fixtures**: 9 shared fixtures
- **Async Tests**: ~25 (tests with `@pytest.mark.asyncio`)
- **Mocked Services**: 5 (Qdrant, Embeddings, AI Agent, Redis, MongoDB)
- **API Endpoints Tested**: 6 endpoints

### Test Execution Time:
- **Unit Tests**: ~2-5 seconds
- **Integration Tests** (mocked): ~1-2 seconds
- **Full Suite**: ~5-10 seconds

## Future Improvements

### Testing Enhancements:
- [ ] **Performance Benchmarks**: Add `pytest-benchmark` for performance regression testing
- [ ] **Load Testing**: Add stress tests for API endpoints using `locust` or `k6`
- [ ] **Property-Based Testing**: Use `hypothesis` for edge case discovery
- [ ] **Mutation Testing**: Add `mutmut` to verify test quality
- [ ] **Contract Testing**: Add Pact tests for API contracts
- [ ] **Security Testing**: Add OWASP security scans

### Coverage Improvements:
- [ ] Increase integration test coverage (currently skipped in CI)
- [ ] Add more edge case tests for coordinate handling
- [ ] Add tests for concurrent case processing
- [ ] Add error recovery tests

### Infrastructure:
- [ ] Add test data generators/factories using `factory_boy`
- [ ] Add database fixtures with real test data
- [ ] Add visual regression testing for reports
- [ ] Set up automated coverage tracking and badges
