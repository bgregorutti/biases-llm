"""
FastAPI main application for LLM Bias Testing
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from biases_llm.config import config_manager
from biases_llm.api.routes import router

# Create FastAPI app
app = FastAPI(
    title="LLM Bias Testing API",
    description="API for testing and comparing biases across different language models",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config_manager.settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Mount static files for frontend
if config_manager.frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(config_manager.frontend_dir), html=True), name="frontend")


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    print("=" * 60)
    print("LLM Bias Testing Application Starting...")
    print("=" * 60)

    # Load and validate configuration
    validation = config_manager.validate_config()

    # Print warnings
    if validation["warnings"]:
        print("\nWarnings:")
        for warning in validation["warnings"]:
            print(f"  ⚠️  {warning}")

    # Print errors (if any)
    if validation["errors"]:
        print("\nErrors:")
        for error in validation["errors"]:
            print(f"  ❌ {error}")

    # Load models configuration
    models_config = config_manager.load_models_config()
    available_models = [m for m in models_config.get("models", []) if m.get("available", False)]
    unavailable_models = [m for m in models_config.get("models", []) if not m.get("available", False)]

    print(f"\n📊 Models Configuration:")
    print(f"  ✅ Available models: {len(available_models)}")
    for model in available_models:
        print(f"     - {model['name']} ({model['id']})")

    if unavailable_models:
        print(f"  ❌ Unavailable models: {len(unavailable_models)}")
        for model in unavailable_models:
            reason = "Missing API key" if model.get("requires_api_key") else "Endpoint not configured"
            print(f"     - {model['name']} ({model['id']}) - {reason}")

    # Load bias prompts
    bias_prompts = config_manager.load_bias_prompts()
    print(f"\n📝 Bias Test Prompts: {len(bias_prompts)} loaded")

    print("\n" + "=" * 60)
    print("🚀 Application ready!")
    print(f"📖 API Documentation: http://localhost:{config_manager.settings.backend_port}/docs")
    print(f"🌐 Frontend: http://localhost:{config_manager.settings.backend_port}/")
    print("=" * 60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    print("\n👋 Shutting down LLM Bias Testing Application...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=config_manager.settings.backend_port
    )
