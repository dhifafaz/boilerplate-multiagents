"""
Pytest configuration and shared fixtures for the test suite.
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import pytz


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_location_details():
    """Sample location details for testing."""
    return {
        "district_name": "PONDOK AREN",
        "city_name": "KOTA TANGERANG SELATAN",
        "district_code": "367403",
        "subdistrict_name": "PARIGI BARU",
        "subdistrict_code": "3674031009",
        "city_code": "3674",
        "province_code": "36",
        "province_name": "BANTEN",
        "country_coordinate": {
            "lat": -6.226229803341365,
            "lon": 106.86878065255794
        },
        "country_name": "Indonesia",
        "country_code3": "IDN",
        "coordinate_subdistrict": {
            "lon": 106.6863014088721,
            "lat": -6.270888106641258
        },
        "coordinate_city": {
            "lon": 106.707384985857,
            "lat": -6.302120075748746
        },
        "coordinate_district": {
            "lon": 106.7112203347439,
            "lat": -6.2663819961069755
        },
        "coordinate_province": {
            "lon": 106.12247277629737,
            "lat": -6.454388616009747
        },
        "coordinate": {
            "lat": -6.2680494,
            "lon": 106.68715499999999
        },
        "address": "Jl. H. Rasam No.96, Parigi Baru",
        "name": "PT. Indonesia Indicator",
        "source": "google maps"
    }


@pytest.fixture
def sample_case_data(sample_location_details):
    """Sample case data for testing."""
    return {
        "input": "Ada ledakan di dekat gedung XYZ",
        "report_summary": "Ledakan di gedung XYZ",
        "report_reliability_score": 80.0,
        "raw_message": "Ada ledakan di dekat gedung XYZ sehingga bisa jadi ada korban",
        "coordinate": [106.6866956, -6.2677857],
        "location_details": sample_location_details,
        "images": [{"url": "https://example.com/image1.jpg"}],
        "audios": [],
        "videos": [],
        "files": [],
        "first_name": "Test",
        "username": "testuser",
        "created_at": "2025-10-20 10:30:00 +0700",
        "sketch": "https://example.com/sketch.png"
    }


@pytest.fixture
def sample_input_data_model(sample_case_data):
    """Sample InputDataModel for API testing."""
    from source.models.api_models import InputDataModel, CaseDataModel
    
    return {
        "score_threshold": 0.85,
        "limit": 5,
        "radius_coordinate": 300.0,
        "report_type": "BOM",
        "data": sample_case_data
    }


@pytest.fixture
def mock_qdrant_client():
    """Mock Qdrant client for testing."""
    mock_client = AsyncMock()
    mock_client.search = AsyncMock(return_value=[])
    mock_client.upsert = AsyncMock(return_value=None)
    mock_client.scroll = AsyncMock(return_value=([], None))
    return mock_client


@pytest.fixture
def mock_embeddings():
    """Mock embeddings service for testing."""
    mock = AsyncMock()
    mock.aembed_query = AsyncMock(return_value=[0.1] * 768)
    return mock


@pytest.fixture
def mock_case_naming_agent():
    """Mock case naming agent for testing."""
    mock = AsyncMock()
    mock.run = AsyncMock(return_value="Test Case Name")
    return mock


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    mock = Mock()
    mock.get = Mock(return_value=None)
    mock.set = Mock(return_value=True)
    mock.delete = Mock(return_value=True)
    return mock


@pytest.fixture
def mock_mongo():
    """Mock MongoDB client for testing."""
    mock = Mock()
    mock.get_by_id = Mock(return_value=None)
    mock.create_by_id = Mock(return_value="test_id")
    mock.update_by_id = Mock(return_value=True)
    mock.delete_by_id = Mock(return_value=True)
    return mock
