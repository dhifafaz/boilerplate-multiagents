"""
Integration tests for the complete workflow.
These tests require actual services running (Qdrant, embeddings, LLM).
Skip these tests in CI/CD if services are not available.
"""
import pytest
from unittest.mock import patch, AsyncMock, Mock


@pytest.mark.integration
@pytest.mark.skipif(True, reason="Requires actual services running")
class TestIntegrationWorkflow:
    """Integration tests for complete workflows."""
    
    @pytest.mark.asyncio
    async def test_complete_case_processing_workflow(self, sample_case_data):
        """Test complete workflow from API to database."""
        from fastapi.testclient import TestClient
        from source.services.api import app
        
        client = TestClient(app)
        
        # Process a new case
        response = client.post("/process-case", json={
            "score_threshold": 0.85,
            "limit": 5,
            "radius_coordinate": 300.0,
            "report_type": "BOM",
            "data": sample_case_data
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "case_id" in data
        
        case_id = data["case_id"]
        
        # Verify we can retrieve the report
        report_response = client.post("/report/latest", json={
            "case_id": case_id,
            "limit": 10
        })
        
        # May return 200 or 404 depending on timing
        assert report_response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_similarity_detection_workflow(self, sample_case_data):
        """Test similarity detection across multiple reports."""
        from source.case_similarity import CaseSimilarityProcessor
        
        processor = CaseSimilarityProcessor()
        
        # Process first report
        result1, count1 = await processor.process_data(
            data=sample_case_data,
            score_threshold=0.85,
            limit=5,
            radius_coordinate=300.0,
            report_type="BOM"
        )
        
        assert result1 is not None
        case_id_1 = result1["id_case"]
        
        # Process similar report
        similar_data = sample_case_data.copy()
        similar_data["input"] = "Ledakan lain di area yang sama"
        similar_data["created_at"] = "2025-10-20 10:35:00 +0700"
        
        result2, count2 = await processor.process_data(
            data=similar_data,
            score_threshold=0.85,
            limit=5,
            radius_coordinate=300.0,
            report_type="BOM"
        )
        
        assert result2 is not None
        # Should link to the same case if similar enough
        # (depends on actual similarity calculation)
        
        case_id_2 = result2["id_case"]
        
        # check if case IDs are the same or different based on similarity
        if count2 > 0:
            assert case_id_1 == case_id_2
        else:
            assert case_id_1 != case_id_2
            assert count2 == 0


@pytest.mark.unit
class TestMockedIntegration:
    """Integration-style tests with mocked services."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_with_mocks(self, sample_case_data):
        """Test end-to-end workflow with all services mocked."""
        from source.case_similarity import CaseSimilarityProcessor
        
        with patch('source.case_similarity.AsyncQdrantService') as mock_qdrant, \
             patch('source.case_similarity.EbdeskTEIEmbeddings') as mock_emb, \
             patch('source.case_similarity.CaseNamingAgent') as mock_agent:
            
            # Setup mocks
            mock_qdrant_instance = AsyncMock()
            mock_qdrant_instance.search = AsyncMock(return_value=[])
            mock_qdrant_instance.upsert = AsyncMock()
            mock_qdrant.return_value = mock_qdrant_instance
            
            mock_emb_instance = AsyncMock()
            mock_emb_instance.aembed_query = AsyncMock(return_value=[0.1] * 768)
            mock_emb.return_value = mock_emb_instance
            
            mock_agent_instance = AsyncMock()
            mock_agent_instance.run = AsyncMock(return_value="Test Case Name")
            mock_agent.return_value = mock_agent_instance
            
            # Run processor
            processor = CaseSimilarityProcessor()
            result, count = await processor.process_data(
                data=sample_case_data,
                score_threshold=0.85,
                limit=5,
                radius_coordinate=300.0,
                report_type="BOM"
            )
            
            # Verify results
            assert result is not None
            assert "id_case" in result
            assert result["case_name"] == "Test Case Name"
            assert count == 0  # No similar cases in mock
            
            # Verify mocks were called
            mock_qdrant_instance.search.assert_called_once()
            mock_qdrant_instance.upsert.assert_called_once()
            mock_emb_instance.aembed_query.assert_called()
            mock_agent_instance.run.assert_called_once()
