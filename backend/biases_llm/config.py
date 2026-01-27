"""
Configuration management for the LLM Bias Testing application
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Keys
    openai_api_key: Optional[str] = Field(None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, alias="ANTHROPIC_API_KEY")

    # Local Model Endpoints
    lm_studio_endpoint: str = Field("http://localhost:1234/v1", alias="LM_STUDIO_ENDPOINT")
    ollama_endpoint: str = Field("http://localhost:11434/v1", alias="OLLAMA_ENDPOINT")

    # Application Settings
    backend_port: int = Field(8000, alias="BACKEND_PORT")
    max_concurrent_queries: int = Field(5, alias="MAX_CONCURRENT_QUERIES")
    query_timeout_seconds: int = Field(30, alias="QUERY_TIMEOUT_SECONDS")

    # CORS Settings
    cors_origins: List[str] = Field(
        ["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:3000", "http://127.0.0.1:8000"],
        alias="CORS_ORIGINS"
    )

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        populate_by_name = True


class ConfigManager:
    """Manages configuration loading and model availability"""

    def __init__(self):
        self.settings = Settings()
        # Get project root directory (parent of backend folder)
        self.project_root = Path(__file__).parent.parent.parent
        self.config_dir = self.project_root / "config"
        self.frontend_dir = self.project_root / "frontend"
        self.models_config: Dict = {}
        self.bias_prompts: List = []

    def load_models_config(self) -> Dict:
        """Load model configurations from JSON file"""
        config_file = self.config_dir / "default_models.json"

        if not config_file.exists():
            print(f"Warning: Models config file not found at {config_file}")
            return {"models": []}

        try:
            with open(config_file, 'r') as f:
                self.models_config = json.load(f)

            # Update model availability based on API keys and endpoints
            self._update_model_availability()

            return self.models_config
        except Exception as e:
            print(f"Error loading models config: {e}")
            return {"models": []}

    def load_bias_prompts(self) -> List:
        """Load pre-built bias test prompts from JSON file"""
        prompts_file = self.config_dir / "bias_test_prompts_v2.json"

        if not prompts_file.exists():
            print(f"Warning: Bias prompts file not found at {prompts_file}")
            return []

        try:
            with open(prompts_file, 'r') as f:
                data = json.load(f)
                self.bias_prompts = data.get("prompts", [])
            return self.bias_prompts
        except Exception as e:
            print(f"Error loading bias prompts: {e}")
            return []

    def _update_model_availability(self):
        """Update model availability based on API keys and endpoint availability"""
        for model in self.models_config.get("models", []):
            model_id = model.get("id")
            requires_api_key = model.get("requires_api_key", False)
            env_key = model.get("env_key")
            api_type = model.get("api_type")

            # Check if model is available
            if requires_api_key and env_key:
                # Check if API key is set
                api_key = getattr(self.settings, env_key.lower(), None)
                model["available"] = api_key is not None and len(api_key) > 0
            else:
                # For local models, assume available (actual connection check would require network call)
                model["available"] = True

    def get_model_config(self, model_id: str) -> Optional[Dict]:
        """Get configuration for a specific model by ID"""
        if not self.models_config:
            self.load_models_config()

        for model in self.models_config.get("models", []):
            if model.get("id") == model_id:
                return model
        return None

    def get_api_key(self, env_key: str) -> Optional[str]:
        """Get API key from environment"""
        return getattr(self.settings, env_key.lower(), None)

    def get_endpoint(self, endpoint_env: str) -> Optional[str]:
        """Get endpoint URL from environment"""
        return getattr(self.settings, endpoint_env.lower(), None)

    def validate_config(self) -> Dict[str, List[str]]:
        """Validate configuration and return warnings/errors"""
        warnings = []
        errors = []

        # Check if any API keys are configured
        if not self.settings.openai_api_key:
            warnings.append("OpenAI API key not configured - OpenAI models will be unavailable")

        if not self.settings.anthropic_api_key:
            warnings.append("Anthropic API key not configured - Claude models will be unavailable")

        # Check if model config file exists
        if not (self.config_dir / "default_models.json").exists():
            errors.append("Model configuration file not found")

        # Check if bias prompts file exists
        if not (self.config_dir / "bias_test_prompts_v2.json").exists():
            warnings.append("Bias prompts file not found - pre-built tests will be unavailable")

        return {
            "warnings": warnings,
            "errors": errors
        }


# Global config manager instance
config_manager = ConfigManager()
