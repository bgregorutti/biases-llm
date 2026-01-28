"""
OpenAI-compatible adapter for OpenAI API, LM Studio, and Ollama
"""
import time

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from biases_llm.services.llm_adapter import LLMAdapter
from biases_llm.models.schemas import ModelResponse
from biases_llm.config import config_manager


class TransformersAdapter(LLMAdapter):
    """Adapter for transformers"""

    def __init__(self, model_config: dict):
        super().__init__(model_config)

        # Get API key if required
        api_key = None
        if model_config.get("requires_api_key") and model_config.get("env_key"):
            api_key = config_manager.get_api_key(model_config["env_key"])
        else:
            # Use placeholder for local models
            api_key = "not-needed"

        # Get custom endpoint if specified
        base_url = None
        if model_config.get("endpoint_env"):
            base_url = config_manager.get_endpoint(model_config["endpoint_env"])

        # Get the specific model name (for providers that need it)
        self.model_name_param = model_config.get("model_name") or model_config.get("id")

    def validate_config(self) -> bool:
        """Validate that the adapter configuration is correct"""
        if self.model_config.get("requires_api_key"):
            env_key = self.model_config.get("env_key")
            if not env_key:
                return False
            api_key = config_manager.get_api_key(env_key)
            return api_key is not None and len(api_key) > 0
        return True

    async def query(self, prompt: str, temperature: float = 0.7) -> ModelResponse:
        """
        Query the OpenAI-compatible API

        Args:
            prompt: The prompt to send to the LLM
            temperature: Temperature parameter for generation

        Returns:
            ModelResponse with result or error
        """
        start_time = time.time()

        try:

            model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name_param)
            tokenizer = AutoTokenizer.from_pretrained(self.model_name_param)

            inputs = tokenizer(prompt, return_tensors="pt")
            outputs = model.generate(**inputs)
            response_text = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]

            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)

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
            elif "connection" in error_msg.lower() or "refused" in error_msg.lower():
                error_msg = f"Connection refused: Model not running or endpoint unreachable"
            elif "timeout" in error_msg.lower():
                error_msg = "Request timeout: Model took too long to respond"
            elif "rate limit" in error_msg.lower():
                error_msg = "Rate limit exceeded: Please wait before making more requests"

            return ModelResponse(
                model_id=self.model_id,
                model_name=self.model_name,
                response=None,
                latency_ms=latency_ms,
                error=error_msg
            )
