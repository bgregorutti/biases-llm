"""
LLM Orchestrator for coordinating parallel queries to multiple models
"""
import asyncio
from typing import List
from datetime import datetime
from backend.models.schemas import ModelResponse, ComparisonResponse
from backend.services.llm_adapter import LLMAdapter
from backend.services.openai_adapter import OpenAIAdapter
from backend.services.anthropic_adapter import AnthropicAdapter
from backend.config import config_manager


class LLMOrchestrator:
    """Coordinates parallel queries to multiple LLM models"""

    def __init__(self):
        self.adapters_cache = {}

    def _get_adapter(self, model_id: str) -> LLMAdapter:
        """
        Get or create an adapter for a specific model

        Args:
            model_id: The model identifier

        Returns:
            LLMAdapter instance for the model
        """
        # Check cache first
        if model_id in self.adapters_cache:
            return self.adapters_cache[model_id]

        # Get model configuration
        model_config = config_manager.get_model_config(model_id)
        if not model_config:
            raise ValueError(f"Model {model_id} not found in configuration")

        # Create appropriate adapter based on API type
        api_type = model_config.get("api_type")

        if api_type == "openai":
            adapter = OpenAIAdapter(model_config)
        elif api_type == "anthropic":
            adapter = AnthropicAdapter(model_config)
        else:
            raise ValueError(f"Unsupported API type: {api_type}")

        # Validate configuration
        if not adapter.validate_config():
            raise ValueError(f"Invalid configuration for model {model_id}")

        # Cache the adapter
        self.adapters_cache[model_id] = adapter

        return adapter

    async def _query_single_model(
        self,
        model_id: str,
        prompt: str,
        temperature: float,
        timeout: int = 30
    ) -> ModelResponse:
        """
        Query a single model with timeout protection

        Args:
            model_id: The model identifier
            prompt: The prompt to send
            temperature: Temperature parameter
            timeout: Timeout in seconds

        Returns:
            ModelResponse with result or error
        """
        try:
            # Get adapter
            adapter = self._get_adapter(model_id)

            # Query with timeout
            response = await asyncio.wait_for(
                adapter.query(prompt, temperature),
                timeout=timeout
            )

            return response

        except asyncio.TimeoutError:
            # Get model info for error response
            model_config = config_manager.get_model_config(model_id)
            model_name = model_config.get("name", model_id) if model_config else model_id

            return ModelResponse(
                model_id=model_id,
                model_name=model_name,
                response=None,
                latency_ms=timeout * 1000,
                error=f"Request timeout: Model took longer than {timeout} seconds"
            )

        except Exception as e:
            # Get model info for error response
            model_config = config_manager.get_model_config(model_id)
            model_name = model_config.get("name", model_id) if model_config else model_id

            return ModelResponse(
                model_id=model_id,
                model_name=model_name,
                response=None,
                latency_ms=0,
                error=str(e)
            )

    async def query_models(
        self,
        prompt: str,
        model_ids: List[str],
        temperature: float = 0.7
    ) -> ComparisonResponse:
        """
        Query multiple models in parallel

        Args:
            prompt: The prompt to send to all models
            model_ids: List of model IDs to query
            temperature: Temperature parameter for generation

        Returns:
            ComparisonResponse with all model responses
        """
        # Get timeout from config
        timeout = config_manager.settings.query_timeout_seconds

        # Create tasks for parallel execution
        tasks = [
            self._query_single_model(model_id, prompt, temperature, timeout)
            for model_id in model_ids
        ]

        # Execute all queries in parallel
        responses = await asyncio.gather(*tasks, return_exceptions=False)

        # Create comparison response
        return ComparisonResponse(
            prompt=prompt,
            timestamp=datetime.utcnow().isoformat() + "Z",
            responses=responses
        )

    def clear_cache(self):
        """Clear the adapter cache"""
        self.adapters_cache = {}


# Global orchestrator instance
orchestrator = LLMOrchestrator()
