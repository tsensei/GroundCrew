![GroundCrew](assets/cover.png)

# GroundCrew

A sequential multi-agent fact-checking system that grounds claims in evidence. Built with LangGraph, OpenAI, and Tavily.

## What It Does

GroundCrew automatically fact-checks text by:
1. **Extracting** factual claims from input
2. **Searching** for evidence via web search
3. **Verifying** claims against evidence
4. **Reporting** findings with confidence scores

## Quick Start

```bash
# Install
poetry install

# Configure API keys
cp env.template .env
# Add your OpenAI and Tavily keys to .env

# Run with text
poetry shell
python main.py "Your text to fact-check"

# Or run with URL (requires FIRECRAWL_API_KEY)
python main.py --url https://example.com/article
```

## Usage

### Python API

```python
from groundcrew.workflow import run_fact_check

result = run_fact_check(
    input_text="The Eiffel Tower is 330 meters tall.",
    openai_api_key="sk-...",
    tavily_api_key="tvly-..."
)

print(result.final_report)
```

### CLI with URL Scraping

```bash
# Fact-check a web page
python main.py --url https://example.com/article

# With custom output and model
python main.py -u https://example.com/article -o report.md --model gpt-4

# Combine with Wikipedia-only mode
python main.py --url https://example.com/article --wikipedia-only
```

## Documentation

Complete documentation is available in the [wiki](wiki/):

- **[Getting Started](wiki/Getting-Started.md)** - Installation and first steps
- **[Usage Guide](wiki/Usage-Guide.md)** - CLI and Python API usage
- **[Architecture](wiki/Architecture.md)** - System design and how it works
- **[API Reference](wiki/API-Reference.md)** - Models and configuration
- **[Examples](wiki/Examples.md)** - Code examples and use cases
- **[Development](wiki/Development.md)** - Contributing and extending
- **[Troubleshooting](wiki/Troubleshooting.md)** - Common issues and solutions

## Features

- ✅ Sequential 4-stage pipeline using LangGraph
- ✅ Structured output with Pydantic validation
- ✅ Type-safe throughout with full type hints
- ✅ Real-time web search via Tavily
- ✅ URL scraping with Firecrawl integration
- ✅ Configurable quality presets
- ✅ Comprehensive test coverage

## Performance

Evaluated on FEVER dataset (100 samples, GPT-4o):

| Configuration | Overall | SUPPORTS | REFUTES | NOT ENOUGH INFO |
|---------------|---------|----------|---------|-----------------|
| Web Search    | 71%     | 88%      | 82%     | 42%             |
| Wikipedia-only| 72%     | 91%      | 88%     | 36%             |

See [`evals/`](evals/) for evaluation scripts and detailed results.

## Technology Stack

- **LangGraph** - Workflow orchestration
- **LangChain** - LLM framework  
- **OpenAI GPT** - Language models
- **Tavily** - Search API
- **Pydantic** - Data validation
- **Poetry** - Dependency management

## Requirements

- Python 3.12.6
- OpenAI API key ([get one](https://platform.openai.com/api-keys))
- Tavily API key ([get one](https://tavily.com))
- Firecrawl API key ([get one](https://firecrawl.dev)) - optional, required for URL scraping

## License

MIT License - see [LICENSE](LICENSE) file

## Built With

Powered by modern AI tools: [LangGraph](https://github.com/langchain-ai/langgraph), [LangChain](https://github.com/langchain-ai/langchain), [OpenAI](https://openai.com), and [Tavily](https://tavily.com).
