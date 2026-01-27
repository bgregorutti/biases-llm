"""
Anthropic adapter for Claude models
"""
import time
from typing import Optional
from anthropic import AsyncAnthropic
from backend.services.llm_adapter import LLMAdapter
from backend.models.schemas import ModelResponse
from backend.config import config_manager


class AnthropicAdapter(LLMAdapter):
    """Adapter for Anthropic Claude models"""

    def __init__(self, model_config: dict):
        super().__init__(model_config)

        # Get API key
        api_key = None
        if model_config.get("env_key"):
            api_key = config_manager.get_api_key(model_config["env_key"])

        # Initialize Anthropic client
        self.client = AsyncAnthropic(api_key=api_key)

        # Get the specific model name
        self.model_name_param = model_config.get("model_name") or model_config.get("id")

    def validate_config(self) -> bool:
        """Validate that the adapter configuration is correct"""
        env_key = self.model_config.get("env_key")
        if not env_key:
            return False
        api_key = config_manager.get_api_key(env_key)
        return api_key is not None and len(api_key) > 0

    async def query(self, prompt: str, temperature: float = 0.7) -> ModelResponse:
        """
        Query the Anthropic API

        Args:
            prompt: The prompt to send to the LLM
            temperature: Temperature parameter for generation

        Returns:
            ModelResponse with result or error
        """
        start_time = time.time()

        try:
            # Make API call
            response = await self.client.messages.create(
                model=self.model_name_param,
                max_tokens=500,  # Reasonable limit for bias testing
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)

            # Extract response text
            response_text = response.content[0].text

            return ModelResponse(
                model_id=self.model_id,
                model_name=self.model_name,
                response=response_text,
                latency_ms=latency_ms,
                error=None
            )

        except Exception as e:
            # Calculate latency even for errors
            latency_ms = int((time.time() - start_time) * 1000)

            # Determine error message
            error_msg = str(e)

            # Provide user-friendly error messages
            if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
                error_msg = "Authentication failed: Invalid or missing API key"
            elif "rate limit" in error_msg.lower():
                error_msg = "Rate limit exceeded: Please wait before making more requests"
            elif "timeout" in error_msg.lower():
                error_msg = "Request timeout: Model took too long to respond"

            return ModelResponse(
                model_id=self.model_id,
                model_name=self.model_name,
                response=None,
                latency_ms=latency_ms,
                error=error_msg
            )
