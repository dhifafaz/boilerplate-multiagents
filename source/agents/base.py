from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from eb_labs.models.openai import OpenAILike
from config import settings
from source.utils.telemetry import logging
from eb_labs.utils.log import logger


class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(
        self,
        agent_name: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        reasoning_effort: str = 'low'
    ):
        self.agent_name = agent_name
        self.model = OpenAILike(
            id=settings.OPENAI_MODEL_NAME,
            base_url=settings.OPENAI_API_BASE_URL,
            api_key=settings.OPENAI_API_KEY,
            temperature=temperature or settings.LLM_TEMPERATURE,
            top_p=0.95,
            timeout=settings.LLM_TIMEOUT,
            max_tokens=max_tokens or settings.LLM_MAX_TOKENS,
        )
        logger.info(f"Initialized {agent_name}")
    
    @abstractmethod
    async def run(self, *args, **kwargs) -> Dict[str, Any]:
        """Execute the agent's main logic."""
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return agent metadata."""
        return {
            "name": self.agent_name,
            "model": settings.OPENAI_MODEL_NAME,
            "temperature": self.model.temperature,
            "max_tokens": self.model.max_tokens
        }