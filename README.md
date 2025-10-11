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

# Run
poetry shell
python main.py "Your text to fact-check"
```

## Usage

```python
from groundcrew.workflow import run_fact_check

result = run_fact_check(
    input_text="The Eiffel Tower is 330 meters tall.",
    openai_api_key="sk-...",
    tavily_api_key="tvly-..."
)

print(result.final_report)
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
- ✅ Configurable quality presets
- ✅ Comprehensive test coverage

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

## License

MIT License - see [LICENSE](LICENSE) file

## Built With

Powered by modern AI tools: [LangGraph](https://github.com/langchain-ai/langgraph), [LangChain](https://github.com/langchain-ai/langchain), [OpenAI](https://openai.com), and [Tavily](https://tavily.com).
