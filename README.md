# LLM Bias Testing Tool

A web application for testing and comparing biases across different language models. This tool helps students and researchers explore how various LLMs respond to bias-sensitive prompts, aligned with the "Biases in AI" lecture materials.

## Features

- **Multi-Model Comparison**: Query multiple LLMs simultaneously and compare responses side-by-side
- **Flexible LLM Support**: Works with both API-based models (OpenAI, Anthropic) and local models (LM Studio, Ollama)
- **Pre-Built Bias Tests**: Curated prompts covering gender bias, professional bias, cultural bias, and more
- **Visual Analysis**: Automatic highlighting of gendered pronouns and bias indicators
- **Export Capabilities**: Save results as CSV or JSON for further analysis in Pandas/Jupyter
- **No Authentication Required**: Simple setup for educational environments

## Architecture

```
app/
├── backend/           # FastAPI backend
│   ├── main.py       # Application entry point
│   ├── config.py     # Configuration management
│   ├── models/       # Pydantic schemas
│   ├── services/     # LLM adapters and orchestrator
│   ├── api/          # API endpoints
│   └── utils/        # Utility functions
├── frontend/         # Vanilla JavaScript frontend
│   ├── index.html    # Main UI
│   └── js/           # JavaScript modules
├── config/           # Configuration files
│   ├── default_models.json      # Model definitions
│   └── bias_test_prompts.json   # Pre-built test prompts
└── requirements.txt  # Python dependencies
```

## Prerequisites

- Python 3.9 or higher
- (Optional) API keys for cloud-based models
- (Optional) Local LLM server (LM Studio or Ollama)

## Installation

### 1. Clone the Repository

```bash
cd /Users/baptistegregorutti/Documents/Repositories/gitlab/introduction-to-ai/app
```

### 2. Install Python Dependencies

```bash
cd backend
uv sync
source .venv/bin/activate
```

### 3. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys (if using cloud models):

```bash
# Optional: Add API keys if using cloud-based models
OPENAI_API_KEY=sk-your-openai-api-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here

# Optional: Configure local model endpoints
LM_STUDIO_ENDPOINT=http://localhost:1234/v1
OLLAMA_ENDPOINT=http://localhost:11434/v1
```

## Running the Application

### Quick Start (Backend Only)

Start the FastAPI backend server:

```bash
cd backend
python main.py
```

Or using uvicorn directly:

```bash
uvicorn backend.main:app --reload --port 8000
```

The application will be available at:
- **Frontend**: http://localhost:8000/
- **API Documentation**: http://localhost:8000/docs
- **API Endpoints**: http://localhost:8000/api/

### Using Different LLM Providers

#### Option 1: Cloud-Based Models (OpenAI, Anthropic)

1. Add your API keys to `.env`:
   ```bash
   OPENAI_API_KEY=sk-...
   ANTHROPIC_API_KEY=sk-ant-...
   ```

2. Start the backend (API keys will be auto-detected)

3. Select cloud models in the web interface

#### Option 2: Local Models (LM Studio)

1. Download and install [LM Studio](https://lmstudio.ai/)

2. Load a model in LM Studio (e.g., Llama 2, Mistral, etc.)

3. Start the local server in LM Studio:
   - Go to "Local Server" tab
   - Click "Start Server"
   - Note the endpoint (default: http://localhost:1234/v1)

4. Update `.env` if using a different endpoint:
   ```bash
   LM_STUDIO_ENDPOINT=http://localhost:1234/v1
   ```

5. Start the backend and select "LM Studio (Local)" in the interface

#### Option 3: Local Models (Ollama)

1. Install [Ollama](https://ollama.ai/)

2. Pull a model:
   ```bash
   ollama pull llama2
   ollama pull mistral
   ```

3. Ollama runs on http://localhost:11434 by default

4. Start the backend and select Ollama models in the interface

## Usage Guide

### Basic Workflow

1. **Open the Application**: Navigate to http://localhost:8000/

2. **Select Models**: Check the boxes for models you want to compare
   - Green checkboxes = Available models
   - Red "(Unavailable)" = Missing API key or endpoint not configured

3. **Choose a Test**:
   - Click a pre-built bias test button, OR
   - Enter your own custom prompt

4. **Adjust Temperature** (optional):
   - 0.0 = More deterministic
   - 2.0 = More creative/random

5. **Click "Compare Models"**: Wait for results to load

6. **Analyze Results**:
   - View responses side-by-side
   - Gendered pronouns are highlighted in yellow
   - Gender-specific terms are highlighted in pink

7. **Export Data** (optional):
   - Click "Export CSV" for Pandas analysis
   - Click "Export JSON" for programmatic use

### Example Use Cases

#### Testing Gender Bias in Professions

1. Select multiple models (e.g., GPT-4, Claude, local Llama)
2. Click "Professional Association: Doctor" quick test
3. Compare how models complete: "The doctor walked into the room. He..."
4. Note differences in pronoun usage and assumptions

#### Testing Cultural Stereotypes

1. Use the "Cultural Assumptions: Names" test
2. Compare responses to prompts about different names
3. Identify stereotype patterns across models

#### Custom Bias Testing

1. Enter your own prompt testing a specific bias dimension
2. Select models to compare
3. Analyze and export results for research

## Configuration Files

### Model Configuration (`config/default_models.json`)

Add or modify LLM models:

```json
{
  "models": [
    {
      "id": "custom-model",
      "name": "My Custom Model",
      "provider": "lm-studio",
      "api_type": "openai",
      "endpoint_env": "LM_STUDIO_ENDPOINT",
      "model_name": "custom-model-name",
      "requires_api_key": false
    }
  ]
}
```

### Bias Test Prompts (`config/bias_test_prompts.json`)

Add custom bias tests:

```json
{
  "prompts": [
    {
      "id": "custom-test-1",
      "category": "gender_bias",
      "title": "My Custom Test",
      "prompt": "Your test prompt here",
      "description": "What this test evaluates",
      "source": "custom"
    }
  ]
}
```

## API Reference

### Endpoints

#### `GET /api/models`
List all available models with availability status.

**Response:**
```json
{
  "models": [
    {
      "id": "gpt-4",
      "name": "GPT-4",
      "provider": "openai",
      "available": true
    }
  ]
}
```

#### `POST /api/query`
Query multiple models with a prompt.

**Request:**
```json
{
  "prompt": "Complete: The doctor is...",
  "models": ["gpt-4", "claude-sonnet-4"],
  "temperature": 0.7
}
```

**Response:**
```json
{
  "prompt": "Complete: The doctor is...",
  "timestamp": "2026-01-27T15:30:00Z",
  "responses": [
    {
      "model_id": "gpt-4",
      "model_name": "GPT-4",
      "response": "...a highly trained professional...",
      "latency_ms": 1234,
      "error": null
    }
  ]
}
```

#### `GET /api/bias-prompts`
Get pre-built bias test prompts.

**Response:**
```json
{
  "prompts": [
    {
      "id": "gender-profession-doctor",
      "category": "gender_bias",
      "title": "Professional Association: Doctor",
      "prompt": "Complete this sentence...",
      "description": "Tests gender stereotypes..."
    }
  ]
}
```

#### `GET /api/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-27T15:30:00Z",
  "available_models": 3
}
```

## Troubleshooting

### Backend won't start

**Error: "Models config file not found"**
- Ensure `config/default_models.json` exists
- Check file path is correct relative to backend directory

**Error: "No module named 'fastapi'"**
- Run `pip install -r requirements.txt`
- Ensure you're using Python 3.9+

### Models showing as unavailable

**Cloud models (OpenAI, Anthropic)**
- Check API keys are correctly set in `.env`
- Verify API key format (starts with `sk-` for OpenAI, `sk-ant-` for Anthropic)
- Test API key with: `curl https://api.openai.com/v1/models -H "Authorization: Bearer YOUR_KEY"`

**Local models (LM Studio, Ollama)**
- Ensure LM Studio or Ollama is running
- Check endpoint URL in `.env` matches the server
- Verify firewall isn't blocking localhost connections

### Query fails or times out

**"Connection refused" error**
- Local model server not running - start LM Studio or Ollama
- Check endpoint URL is correct

**"Request timeout" error**
- Increase timeout in `.env`: `QUERY_TIMEOUT_SECONDS=60`
- Local model may be too slow - try a smaller model
- Reduce max concurrent queries: `MAX_CONCURRENT_QUERIES=3`

**"Rate limit exceeded" error**
- You've hit API rate limits
- Wait a few minutes before retrying
- Consider using local models instead

### Frontend issues

**Models or prompts not loading**
- Check browser console for errors (F12 → Console tab)
- Verify backend is running and accessible
- Check CORS settings in `backend/config.py`

**Results not displaying**
- Check browser console for JavaScript errors
- Ensure all JS files loaded correctly
- Clear browser cache and refresh

## Educational Use

### For Instructors

This tool complements the "Biases in AI" lecture by providing:

1. **Live Demonstrations**: Show real-time bias patterns during lectures
2. **Hands-on Practice**: Students can explore biases independently
3. **Data Collection**: Export results for quantitative analysis
4. **Discussion Starters**: Compare responses to spark classroom discussion

### For Students

Use this tool to:

1. **Explore Bias Dimensions**: Test gender, racial, professional, and cultural biases
2. **Compare Models**: Understand how different architectures handle bias
3. **Collect Data**: Export results for research projects or reports
4. **Analyze Patterns**: Use CSV exports with Pandas for deeper analysis

### Assignment Ideas

1. **Bias Audit**: Test 10 prompts across 3 models, analyze patterns
2. **Prompt Engineering**: Create prompts that reveal specific biases
3. **Comparative Study**: Compare cloud vs. local model bias patterns
4. **Mitigation Analysis**: Test debiased vs. standard models

## Advanced Configuration

### Adding New LLM Providers

1. Create a new adapter in `backend/services/`:

```python
from backend.services.llm_adapter import LLMAdapter
from backend.models.schemas import ModelResponse

class CustomAdapter(LLMAdapter):
    async def query(self, prompt: str, temperature: float) -> ModelResponse:
        # Your implementation
        pass
```

2. Register in `backend/services/llm_orchestrator.py`

3. Add model configuration to `config/default_models.json`

### Custom Bias Detection

Modify `frontend/js/comparison-view.js` to add custom highlighting:

```javascript
highlightBiasIndicators(text) {
    // Add your custom detection logic
    // Example: highlight specific keywords, sentiment, etc.
}
```

## Performance Considerations

- **Parallel Queries**: Queries to different models run simultaneously
- **Timeouts**: Default 30s per model (configurable)
- **Rate Limiting**: Respect API provider rate limits
- **Local Models**: Generally slower but no rate limits

## Security Notes

- **API Keys**: Never commit `.env` file to version control
- **Local Only**: Default configuration only allows localhost access
- **No Authentication**: Suitable for local/educational use only
- **Production**: Add authentication and rate limiting for public deployment

## Contributing

To extend this tool:

1. Add new bias test prompts to `config/bias_test_prompts.json`
2. Create new LLM adapters for additional providers
3. Enhance bias detection algorithms in frontend
4. Add new export formats (PDF, Excel, etc.)

## License

Educational use only. Part of the "Introduction to AI" course materials.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review API documentation at http://localhost:8000/docs
3. Contact course instructors

## Acknowledgments

- Based on "Biases in Language Models" lecture (biases.tex)
- Built with FastAPI, Tailwind CSS, and vanilla JavaScript
- Supports OpenAI, Anthropic, LM Studio, and Ollama
