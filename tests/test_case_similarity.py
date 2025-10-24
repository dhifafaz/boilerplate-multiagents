"""
Unit tests for CaseSimilarityProcessor class.
"""
import pytest
import hashlib
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from qdrant_client import models

from source.case_similarity import CaseSimilarityProcessor


class TestCaseSimilarityProcessor:
    """Test suite for CaseSimilarityProcessor."""
    
    @pytest.fixture
    def processor(self, mock_qdrant_client, mock_embeddings, mock_case_naming_agent):
        """Create a processor instance with mocked dependencies."""
        with patch('source.case_similarity.AsyncQdrantService') as mock_qdrant, \
             patch('source.case_similarity.EbdeskTEIEmbeddings') as mock_emb, \
             patch('source.case_similarity.CaseNamingAgent') as mock_agent:
            
            mock_qdrant.return_value = mock_qdrant_client
            mock_emb.return_value = mock_embeddings
            mock_agent.return_value = mock_case_naming_agent
            
            processor = CaseSimilarityProcessor()
            processor.qdrant_client = mock_qdrant_client
            processor.embeddings = mock_embeddings
            processor.case_naming_agent = mock_case_naming_agent
            
            return processor
    
    def test_generate_case_id(self, processor):
        """Test case ID generation format."""
        case_id = processor._generate_case_id(
            category="BOM",
            location_code="TSL",
            date_str="202510",
            daily_index="01",
            unique_string="test-string"
        )
        
        assert case_id.startswith("BOM-TSL-202510-01-")
        assert len(case_id.split("-")[-1]) == 4  # Hash part should be 4 chars
    
    def test_normalize_coordinate(self, processor):
        """Test coordinate normalization."""
        # Test with lon field
        coord = {"lat": -6.2680494, "lon": 106.68715499999999}
        normalized = processor._normalize_coordinate(coord)
        assert normalized == {"lat": -6.2680494, "lon": 106.68715499999999}
        
        # Test with long field
        coord = {"lat": -6.2680494, "long": 106.68715499999999}
        normalized = processor._normalize_coordinate(coord)
        assert normalized == {"lat": -6.2680494, "lon": 106.68715499999999}
        
        # Test with None
        assert processor._normalize_coordinate(None) is None
    
    def test_extract_location_data(self, processor, sample_case_data):
        """Test location data extraction."""
        location_data = processor._extract_location_data(sample_case_data)
        
        assert location_data["subdistrict_code"] == "3674031009"
        assert location_data["district_code"] == "367403"
        assert location_data["city_code"] == "3674"
        assert location_data["province_code"] == "36"
        assert location_data["raw_coordinate"] is not None
    
    def test_create_qdrant_filter(self, processor):
        """Test Qdrant filter creation."""
        coordinate = {"lat": -6.2680494, "lon": 106.68715}
        timestamp = 1729400000
        
        qdrant_filter = processor._create_qdrant_filter(
            coordinate=coordinate,
            timestamp=timestamp,
            coordinate_max_radius=300.0,
            subdistrict_code="3674031009"
        )
        
        assert isinstance(qdrant_filter, models.Filter)
        assert len(qdrant_filter.must) == 3  # coordinate, timestamp, subdistrict
    
    def test_format_report(self, processor, sample_case_data):
        """Test report formatting."""
        formatted = processor._format_report(sample_case_data)
        
        assert "Report Type:" in formatted
        assert "Summary:" in formatted
        assert "Input:" in formatted
        assert "Location Details:" in formatted
    
    @pytest.mark.asyncio
    async def test_generate_case_name(self, processor, sample_case_data):
        """Test case name generation."""
        processor.case_naming_agent.run = AsyncMock(return_value="Test Case Name")
        
        case_name = await processor._generate_case_name(sample_case_data)
        
        assert case_name == "Test Case Name"
        processor.case_naming_agent.run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_find_similar_data(self, processor, mock_qdrant_client):
        """Test finding similar data."""
        # Mock search results
        mock_hit = Mock()
        mock_hit.score = 0.95
        mock_hit.payload = {
            "id_case": "BOM-TSL-202510-01-ABCD",
            "case_name": "Test Case",
            "metadata": {"test": "data"}
        }
        
        mock_qdrant_client.search = AsyncMock(return_value=[mock_hit])
        
        result = await processor._find_similar_data(
            text="test text",
            qdrant_filter=None,
            score_threshold=0.8,
            limit=5
        )
        
        assert len(result) == 1
        assert result[0]["similarity_score"] == 0.95
        assert result[0]["payload"]["id_case"] == "BOM-TSL-202510-01-ABCD"
    
    @pytest.mark.asyncio
    async def test_insert_to_qdrant(self, processor, mock_qdrant_client):
        """Test inserting data to Qdrant."""
        data = {
            "id": "test-id",
            "text": "test text",
            "input": "test input",
            "case_name": "Test Case",
            "id_case": "BOM-TSL-202510-01-ABCD",
            "coordinate": {"lat": -6.268, "lon": 106.687},
            "timestamp": 1729400000
        }
        
        await processor._insert_to_qdrant(data)
        
        mock_qdrant_client.upsert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_data_new_case(self, processor, sample_case_data, mock_qdrant_client):
        """Test processing data for a new case (no similar cases found)."""
        # Mock no similar cases found
        mock_qdrant_client.search = AsyncMock(return_value=[])
        processor.case_naming_agent.run = AsyncMock(return_value="New Case Name")
        
        result, similar_count = await processor.process_data(
            data=sample_case_data,
            score_threshold=0.85,
            limit=5,
            radius_coordinate=300.0,
            report_type="BOM"
        )
        
        assert result is not None
        assert similar_count == 0
        assert result["case_name"] == "New Case Name"
        assert "id_case" in result
        assert result["id_case"].startswith("BOM-")
    
    @pytest.mark.asyncio
    async def test_process_data_existing_case(self, processor, sample_case_data, mock_qdrant_client):
        """Test processing data for an existing case (similar cases found)."""
        # Mock similar case found
        mock_hit = Mock()
        mock_hit.score = 0.95
        mock_hit.payload = {
            "id_case": "BOM-TSL-202510-01-ABCD",
            "case_name": "Existing Case Name",
            "metadata": {"test": "data"}
        }
        
        mock_qdrant_client.search = AsyncMock(return_value=[mock_hit])
        
        result, similar_count = await processor.process_data(
            data=sample_case_data,
            score_threshold=0.85,
            limit=5,
            radius_coordinate=300.0,
            report_type="BOM"
        )
        
        assert result is not None
        assert similar_count == 1
        assert result["case_name"] == "Existing Case Name"
        assert result["id_case"] == "BOM-TSL-202510-01-ABCD"
    
    @pytest.mark.asyncio
    async def test_get_reports_by_case_id(self, processor, mock_qdrant_client):
        """Test getting reports by case ID."""
        # Mock scroll results
        mock_point = Mock()
        mock_point.payload = {
            "metadata": {
                "id": "report-1",
                "id_case": "BOM-TSL-202510-01-ABCD",
                "input": "Test report",
                "timestamp": 1729400000
            }
        }
        
        mock_qdrant_client.scroll = AsyncMock(return_value=([mock_point], None))
        
        reports = await processor.get_reports_by_case_id(
            case_id="BOM-TSL-202510-01-ABCD",
            start_timestamp=1729300000,
            end_timestamp=1729500000,
            limit=100
        )
        
        assert len(reports) == 1
        assert reports[0]["id_case"] == "BOM-TSL-202510-01-ABCD"
