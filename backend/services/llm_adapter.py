"""
Base adapter interface for LLM providers
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional
from backend.models.schemas import ModelResponse


class LLMAdapter(ABC):
    """Abstract base class for LLM adapters"""

    def __init__(self, model_config: Dict):
        """
        Initialize the adapter with model configuration

        Args:
            model_config: Dictionary containing model configuration
        """
        self.model_config = model_config
        self.model_id = model_config.get("id")
        self.model_name = model_config.get("name")

    @abstractmethod
    async def query(self, prompt: str, temperature: float = 0.7) -> ModelResponse:
        """
        Query the LLM with a prompt

        Args:
            prompt: The prompt to send to the LLM
            temperature: Temperature parameter for generation (0.0 to 2.0)

        Returns:
            ModelResponse containing the result or error
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate that the adapter configuration is correct

        Returns:
            True if configuration is valid, False otherwise
        """
        pass

    def get_model_info(self) -> Dict:
        """
        Get information about this model

        Returns:
            Dictionary with model metadata
        """
        return {
            "id": self.model_id,
            "name": self.model_name,
            "provider": self.model_config.get("provider"),
            "api_type": self.model_config.get("api_type"),
        }
