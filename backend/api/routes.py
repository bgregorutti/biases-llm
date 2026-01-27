"""
API routes for the LLM Bias Testing application
"""
from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from backend.models.schemas import (
    QueryRequest,
    ComparisonResponse,
    ModelsListResponse,
    ModelConfig,
    BiasPromptsResponse,
    BiasPrompt,
    HealthResponse
)
from backend.config import config_manager
from backend.services.llm_orchestrator import orchestrator

router = APIRouter(prefix="/api")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    models_config = config_manager.load_models_config()
    available_count = sum(1 for m in models_config.get("models", []) if m.get("available", False))

    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat() + "Z",
        available_models=available_count
    )


@router.get("/models", response_model=ModelsListResponse)
async def get_models():
    """Get list of available LLM models"""
    models_config = config_manager.load_models_config()

    # Convert to ModelConfig objects
    models = [
        ModelConfig(**model)
        for model in models_config.get("models", [])
    ]

    return ModelsListResponse(models=models)


@router.post("/query", response_model=ComparisonResponse)
async def query_models(request: QueryRequest):
    """
    Query multiple LLM models with the same prompt

    Args:
        request: QueryRequest containing prompt, model IDs, and temperature

    Returns:
        ComparisonResponse with results from all models
    """
    # Validate that at least one model is requested
    if not request.models or len(request.models) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one model must be specified"
        )

    # Validate that all requested models exist
    models_config = config_manager.load_models_config()
    available_model_ids = {m["id"] for m in models_config.get("models", [])}

    invalid_models = [m for m in request.models if m not in available_model_ids]
    if invalid_models:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid model IDs: {', '.join(invalid_models)}"
        )

    # Query all models in parallel
    try:
        result = await orchestrator.query_models(
            prompt=request.prompt,
            model_ids=request.models,
            temperature=request.temperature
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying models: {str(e)}"
        )


@router.get("/bias-prompts", response_model=BiasPromptsResponse)
async def get_bias_prompts():
    """Get pre-built bias test prompts"""
    prompts_data = config_manager.load_bias_prompts()

    # Convert to BiasPrompt objects
    prompts = [
        BiasPrompt(**prompt)
        for prompt in prompts_data
    ]

    return BiasPromptsResponse(prompts=prompts)
