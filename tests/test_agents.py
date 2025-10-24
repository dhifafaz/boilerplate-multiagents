"""
Unit tests for agent classes.
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch

from source.agents.case_name_extractor.agent import CaseNamingAgent, CaseNamingOutput
from source.agents.base import BaseAgent


class TestCaseNamingAgent:
    """Test suite for CaseNamingAgent."""
    
    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent with mocked dependencies."""
        with patch('source.agents.case_name_extractor.agent.Agent') as mock_agent_class, \
             patch('source.agents.base.OpenAILike') as mock_openai:
            
            # Mock OpenAILike to return a mock model
            mock_model = Mock()
            mock_model.temperature = 0.3
            mock_model.max_tokens = 1000
            mock_openai.return_value = mock_model
            
            mock_agent_instance = AsyncMock()
            mock_agent_class.return_value = mock_agent_instance
            
            agent = CaseNamingAgent()
            agent.agent = mock_agent_instance
            
            return agent
    
    @pytest.mark.asyncio
    async def test_run_success(self, mock_agent):
        """Test successful case name generation."""
        # Mock response
        mock_response = Mock()
        mock_response.content = CaseNamingOutput(
            case_name="Ledakan di Gedung XYZ (Tangerang Selatan)"
        )
        mock_agent.agent.arun = AsyncMock(return_value=mock_response)
        
        report = """
        Report Type: BOM
        Summary: Ledakan di gedung XYZ
        Input: Ada ledakan di dekat gedung XYZ
        Location Details: City: TANGERANG SELATAN
        """
        
        case_name = await mock_agent.run(report)
        
        assert case_name == "Ledakan di Gedung XYZ (Tangerang Selatan)"
        mock_agent.agent.arun.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_with_different_reports(self, mock_agent):
        """Test case name generation with different report types."""
        test_cases = [
            ("BOM report", "Ledakan Bom"),
            ("DEMO report", "Aksi Unjuk Rasa"),
            ("FIRE report", "Kebakaran Gedung")
        ]
        
        for report_input, expected_name in test_cases:
            mock_response = Mock()
            mock_response.content = CaseNamingOutput(case_name=expected_name)
            mock_agent.agent.arun = AsyncMock(return_value=mock_response)
            
            case_name = await mock_agent.run(report_input)
            assert case_name == expected_name


class TestBaseAgent:
    """Test suite for BaseAgent."""
    
    def test_base_agent_is_abstract(self):
        """Test that BaseAgent cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseAgent(agent_name="Test Agent")
    
    def test_base_agent_subclass(self):
        """Test creating a valid subclass of BaseAgent."""
        
        class TestAgent(BaseAgent):
            async def run(self):
                return {"result": "test"}
        
        with patch('source.agents.base.OpenAILike'):
            agent = TestAgent(agent_name="Test Agent")
            assert agent.agent_name == "Test Agent"
    
    def test_get_metadata(self):
        """Test metadata retrieval."""
        
        class TestAgent(BaseAgent):
            async def run(self):
                return {"result": "test"}
        
        with patch('source.agents.base.OpenAILike') as mock_model, \
             patch('source.agents.base.settings') as mock_settings:
            
            mock_settings.OPENAI_MODEL_NAME = "gpt-4"
            mock_settings.LLM_TEMPERATURE = 0.3
            mock_settings.LLM_MAX_TOKENS = 1000
            mock_settings.LLM_TIMEOUT = 120
            
            mock_model_instance = Mock()
            mock_model_instance.temperature = 0.3
            mock_model_instance.max_tokens = 1000
            mock_model.return_value = mock_model_instance
            
            agent = TestAgent(agent_name="Test Agent")
            metadata = agent.get_metadata()
            
            assert metadata["name"] == "Test Agent"
            assert "model" in metadata
            assert "temperature" in metadata
            assert "max_tokens" in metadata
