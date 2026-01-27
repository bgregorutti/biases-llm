"""
Pydantic models for request/response schemas
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class QueryRequest(BaseModel):
    """Request schema for querying multiple LLMs"""
    prompt: str = Field(..., description="The prompt to send to LLMs", min_length=1, max_length=5000)
    models: List[str] = Field(..., description="List of model IDs to query", min_items=1)
    temperature: float = Field(default=0.7, description="Temperature for LLM generation", ge=0.0, le=2.0)


class ModelResponse(BaseModel):
    """Response from a single LLM model"""
    model_id: str = Field(..., description="ID of the model")
    model_name: str = Field(..., description="Display name of the model")
    response: Optional[str] = Field(None, description="Generated response from the model")
    latency_ms: int = Field(..., description="Response time in milliseconds")
    error: Optional[str] = Field(None, description="Error message if query failed")


class ComparisonResponse(BaseModel):
    """Aggregated response from multiple LLMs"""
    prompt: str = Field(..., description="The original prompt")
    timestamp: str = Field(..., description="ISO 8601 timestamp of the query")
    responses: List[ModelResponse] = Field(..., description="List of responses from each model")


class ModelConfig(BaseModel):
    """Configuration for an LLM model"""
    id: str = Field(..., description="Unique identifier for the model")
    name: str = Field(..., description="Display name of the model")
    provider: str = Field(..., description="Provider name (openai, anthropic, lm-studio, ollama)")
    api_type: str = Field(..., description="API type (openai, anthropic)")
    requires_api_key: bool = Field(..., description="Whether this model requires an API key")
    env_key: Optional[str] = Field(None, description="Environment variable name for API key")
    endpoint_env: Optional[str] = Field(None, description="Environment variable name for custom endpoint")
    model_name: Optional[str] = Field(None, description="Specific model name for the provider")
    available: bool = Field(default=False, description="Whether the model is currently available")


class ModelsListResponse(BaseModel):
    """Response containing list of available models"""
    models: List[ModelConfig] = Field(..., description="List of available LLM models")


class BiasPrompt(BaseModel):
    """Pre-built bias test prompt"""
    id: str = Field(..., description="Unique identifier for the prompt")
    category: str = Field(..., description="Bias category (gender_bias, racial_bias, professional_bias)")
    title: str = Field(..., description="Short title for the test")
    prompt: str = Field(..., description="The actual prompt text")
    description: str = Field(..., description="Description of what this test evaluates")
    source: Optional[str] = Field(None, description="Source reference (e.g., lecture slide number)")


class BiasPromptsResponse(BaseModel):
    """Response containing list of bias test prompts"""
    prompts: List[BiasPrompt] = Field(..., description="List of pre-built bias test prompts")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Health status")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    available_models: int = Field(..., description="Number of available models")
