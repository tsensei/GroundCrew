# Getting Started

Get up and running with GroundCrew in 5 minutes.

## Prerequisites

- Python 3.12.6
- Poetry ([install](https://python-poetry.org/docs/#installation))
- OpenAI API key
- Tavily API key

## Installation

### 1. Install Dependencies

```bash
cd /path/to/GroundCrew
poetry install
```

This installs all required packages including LangGraph, LangChain, OpenAI client, and Tavily.

### 2. Get API Keys

#### OpenAI API Key
1. Visit https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

#### Tavily API Key
1. Visit https://tavily.com
2. Sign up for a free account
3. Get your API key from the dashboard (starts with `tvly-`)

### 3. Configure Environment

Create a `.env` file in the project root:

```bash
cp env.template .env
```

Edit `.env` and add your API keys:

```bash
OPENAI_API_KEY=sk-your-actual-key-here
TAVILY_API_KEY=tvly-your-actual-key-here
```

**Alternative**: Export directly in your shell:

```bash
export OPENAI_API_KEY="sk-..."
export TAVILY_API_KEY="tvly-..."
```

## First Fact-Check

### Activate Environment

```bash
poetry shell
```

### Run Default Example

```bash
python main.py
```

You should see output like:

```
======================================================================
GROUNDCREW - Automated Fact-Checking Workflow
======================================================================

Pipeline Stages:
----------------------------------------------------------------------
✓ Extracted 4 claims
✓ Retrieved 12 pieces of evidence
✓ Verified 4 claims
✓ Generated final report
----------------------------------------------------------------------

✅ Fact-checking complete!
```

### Try Custom Text

```bash
python main.py "Python was created by Guido van Rossum in 1991."
```

## Using Python API

```python
from groundcrew.workflow import run_fact_check
import os

result = run_fact_check(
    input_text="The Great Wall of China is visible from space.",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    tavily_api_key=os.getenv("TAVILY_API_KEY")
)

print(result.final_report)
```

## Understanding Output

A fact-check report includes:

### 1. Claims Found
List of factual statements extracted from the input

### 2. Verdicts
For each claim:
- **Status**: `SUPPORTS`, `REFUTES`, or `NOT ENOUGH INFO` (FEVER-compliant labels)
- **Confidence**: 0-100% confidence score
- **Justification**: Explanation of the verdict
- **Evidence**: Sources and snippets used

### 3. Final Report
Human-readable summary of all findings

## Example Output

```
[Claim 1] Python was created by Guido van Rossum in 1991.
Status: SUPPORTS (Confidence: 95%)
Justification: Multiple reliable sources confirm that Guido van Rossum 
created Python, with the first version released in 1991.

Evidence (3 sources):
  1. https://en.wikipedia.org/wiki/Python_(programming_language)
     Python is a high-level programming language created by Guido van 
     Rossum and first released in 1991...
```

## Common Issues

### API Key Not Found
```bash
# Check .env file exists
cat .env

# Or export directly
export OPENAI_API_KEY="sk-..."
export TAVILY_API_KEY="tvly-..."
```

### Module Not Found
```bash
# Reinstall dependencies
poetry install

# Activate environment
poetry shell
```

### Slow Performance
This is normal! Each claim requires:
- LLM call to extract claims
- LLM call to generate search queries
- Multiple web searches via Tavily
- LLM call to verify
- LLM call to generate report

Try with simpler/fewer claims first, or use `gpt-4o-mini` for faster results.

## Next Steps

- See [Usage Guide](Usage-Guide.md) for detailed usage
- Read [Architecture](Architecture.md) to understand how it works
- Check [Examples](Examples.md) for more use cases
- Explore [API Reference](API-Reference.md) for customization

## Cost Estimates

Approximate costs per fact-check with 5 claims:

| Model | Cost per Check |
|-------|----------------|
| gpt-4o-mini | $0.01 - 0.05 |
| gpt-4 | $0.10 - 0.30 |

Tavily: ~$0.01 per check (free tier available)

