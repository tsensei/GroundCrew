# TCC Observability for GroundCrew

GroundCrew is now instrumented with TCC observability to track LangGraph agent runs, steps, and tool calls in the TCC dashboard.

## Setup

### 1. Install Dependencies

The required dependency is already included in `pyproject.toml`:

```toml
tcc-otel[langchain] (>=0.1.0,<0.2.0)
```

Install it with:

```bash
poetry install
```

### 2. Get Your TCC API Key

1. Sign up or log in to your TCC account
2. Get your API key from the dashboard
3. Add it to your `.env` file:

```bash
# Copy from env.template if you haven't already
cp env.template .env

# Add your TCC API key
echo "TCC_API_KEY=your-tcc-api-key-here" >> .env
```

### 3. That's It!

The instrumentation is already configured in all entry points:
- `main.py` - CLI entry point
- `demo.py` - Demo script
- `examples/simple_check.py` - Simple example
- `examples/batch_check.py` - Batch processing
- `examples/advanced_config.py` - Advanced configuration
- `examples/url_scraping.py` - URL scraping
- `examples/tcc_metadata_example.py` - Metadata usage examples

## How It Works

The TCC instrumentation is initialized **before** LangGraph and LangChain are imported:

```python
from dotenv import load_dotenv
import os

# Load environment variables FIRST
load_dotenv()

# Import and initialize TCC instrumentation BEFORE importing LangGraph/LangChain
from tcc_otel import instrument_langchain

instrument_langchain(
    api_key=os.getenv("TCC_API_KEY"),
)

# Now import LangGraph/LangChain dependencies
from groundcrew.workflow import run_fact_check
```

This ensures that all LangGraph runs, steps, and tool calls are automatically tracked.

## Using Custom Metadata

Custom metadata allows you to tag agent runs with additional properties for filtering and analysis in the TCC dashboard.

### Basic Usage

Pass a `metadata` dictionary to `run_fact_check()`:

```python
result = run_fact_check(
    input_text="Your text to fact-check",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    tavily_api_key=os.getenv("TAVILY_API_KEY"),
    model_name="gpt-4o-mini",
    # Add custom metadata
    metadata={
        "userId": "user-123",
        "feature": "fact-check",
    }
)
```

### Common Metadata Patterns

#### 1. User Tracking
Tag runs by user for per-user analysis:
```python
metadata={
    "userId": "4a6b111c-b53a-4d00-a877-67185022ab9e",
    "username": "john.doe",
}
```

#### 2. Organization/Multi-tenant
Track usage across organizations:
```python
metadata={
    "organizationId": "acme-corp",
    "department": "research",
    "project": "fact-verification",
}
```

#### 3. Request Context
Add request-level tracking:
```python
metadata={
    "requestId": "req_abc123",
    "sessionId": "sess_xyz789",
    "source": "api",
    "environment": "production",
}
```

#### 4. Content Type
Categorize by content type:
```python
metadata={
    "contentType": "news-article",
    "domain": "politics",
    "priority": "high",
}
```

### Complete Example

See `examples/tcc_metadata_example.py` for comprehensive examples:

```bash
python examples/tcc_metadata_example.py
```

## What Gets Tracked

The TCC instrumentation automatically tracks:

1. **Agent Runs** - Each complete fact-checking pipeline execution
2. **Steps** - Individual nodes in the LangGraph workflow:
   - Claim extraction
   - Evidence search
   - Claim verification
   - Report generation
3. **Tool Calls** - All LLM invocations and tool usage
4. **Custom Metadata** - Your tags for filtering and analysis

## Viewing Results

1. Log in to your TCC dashboard
2. Navigate to the agent runs view
3. Filter by your custom metadata fields
4. Analyze performance, costs, and patterns

## Troubleshooting

### No data appearing in TCC dashboard?

1. **Check your API key**: Make sure `TCC_API_KEY` is set in `.env`
2. **Verify instrumentation order**: TCC must be initialized before LangGraph imports
3. **Check internet connection**: TCC needs to send telemetry data

### Instrumentation errors?

The app will continue to work even if TCC instrumentation fails. Check:

1. `tcc-otel[langchain]` package is installed
2. API key is valid
3. No network/firewall issues

### Missing metadata in dashboard?

Make sure you're passing the `metadata` parameter to `run_fact_check()`:

```python
# ✓ Correct
run_fact_check(..., metadata={"userId": "123"})

# ✗ Wrong - metadata not passed
run_fact_check(...)
```

## Examples

### Run the CLI with tracking
```bash
python main.py "Your claim to fact-check"
```

### Run a simple example
```bash
python examples/simple_check.py
```

### Run the metadata example
```bash
python examples/tcc_metadata_example.py
```

### Run batch processing
```bash
python examples/batch_check.py
```

All of these will automatically send telemetry to TCC!

## Benefits

- **Monitor Performance**: Track latency and costs per user/organization
- **Debug Issues**: See detailed traces of agent runs and tool calls
- **Analyze Usage**: Understand which features are used most
- **Filter & Search**: Find specific runs by custom metadata
- **Track Quality**: Monitor success rates and confidence scores
- **Optimize Costs**: Identify expensive operations and users

## Learn More

- TCC Documentation: [https://docs.tcc.ai](https://docs.tcc.ai)
- LangGraph Documentation: [https://langchain-ai.github.io/langgraph/](https://langchain-ai.github.io/langgraph/)
- GroundCrew README: [README.md](README.md)
