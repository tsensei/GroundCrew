# GroundCrew Wiki

Welcome to the GroundCrew documentation. GroundCrew is an automated fact-checking system that uses a sequential multi-agent pipeline to verify claims with evidence from the web.

## Quick Links

### 📘 Getting Started
- **[Getting Started](Getting-Started.md)** - Installation, setup, and your first fact-check

### 📖 Core Documentation
- **[Usage Guide](Usage-Guide.md)** - CLI and Python API usage
- **[Architecture](Architecture.md)** - System design and how it works
- **[API Reference](API-Reference.md)** - Models, configuration, and methods

### 🛠️ Development
- **[Development Guide](Development.md)** - Contributing, testing, and code style
- **[Troubleshooting](Troubleshooting.md)** - Common issues and solutions

### 💡 Learning
- **[Examples](Examples.md)** - Use cases and code examples

## What is GroundCrew?

GroundCrew implements a **sequential multi-agent pipeline** for automated fact-checking:

1. **Claim Extraction** → Identifies verifiable factual statements
2. **Evidence Retrieval** → Searches for supporting/refuting information via Tavily
3. **Verification** → Analyzes evidence and determines truthfulness  
4. **Reporting** → Generates human-readable fact-check reports

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Orchestration | LangGraph |
| LLM Framework | LangChain |
| Language Model | OpenAI GPT |
| Search API | Tavily |
| Validation | Pydantic |
| Package Manager | Poetry |

## Quick Example

```python
from groundcrew.workflow import run_fact_check

result = run_fact_check(
    input_text="The Eiffel Tower is 330 meters tall.",
    openai_api_key="sk-...",
    tavily_api_key="tvly-..."
)

print(result.final_report)
```

## Key Features

- ✅ Complete end-to-end pipeline
- ✅ Structured output with Pydantic validation
- ✅ Multiple OpenAI models supported
- ✅ Real-time web search
- ✅ Type-safe throughout
- ✅ Configurable quality presets
- ✅ Comprehensive testing

## Navigation

Start with **[Getting Started](Getting-Started.md)** to set up GroundCrew, then explore the other guides as needed.

