# Usage Guide

Complete guide to using GroundCrew for fact-checking.

## Command Line Interface

### Basic Usage

Run with default example:
```bash
python main.py
```

### Custom Text

Check any text by passing it as an argument:
```bash
python main.py "Your claim to fact-check"
```

### Interactive Demo

Run the interactive demo for multiple checks:
```bash
python demo.py
```

## Python API

### Basic Fact-Check

```python
from groundcrew.workflow import run_fact_check
import os

result = run_fact_check(
    input_text="Your text to fact-check",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    tavily_api_key=os.getenv("TAVILY_API_KEY"),
    model_name="gpt-4o-mini"  # optional, default
)

print(result.final_report)
```

### Accessing Results

```python
# Full human-readable report
print(result.final_report)

# All extracted claims
for claim in result.claims:
    print(f"{claim.text} (priority: {claim.priority})")

# Verdicts for each claim
for verdict in result.verdicts:
    print(f"Claim: {verdict.claim}")
    print(f"Status: {verdict.status}")
    print(f"Confidence: {verdict.confidence:.0%}")
    print(f"Justification: {verdict.justification}")

# Evidence collected
for claim_text, evidence_list in result.evidence_map.items():
    print(f"Evidence for: {claim_text}")
    for ev in evidence_list:
        print(f"  Source: {ev.source}")
        print(f"  Snippet: {ev.snippet[:100]}...")
```

## Model Selection

### Available Models

```python
# Fast and cheap (recommended for most use cases)
model_name="gpt-4o-mini"

# High quality
model_name="gpt-4"

# Faster GPT-4
model_name="gpt-4-turbo"
```

### Model Comparison

| Model | Speed | Quality | Cost per Check (5 claims) |
|-------|-------|---------|---------------------------|
| gpt-4o-mini | ⚡⚡⚡ | ⭐⭐⭐ | $0.01 - 0.05 |
| gpt-4-turbo | ⚡⚡ | ⭐⭐⭐⭐ | $0.08 - 0.25 |
| gpt-4 | ⚡ | ⭐⭐⭐⭐⭐ | $0.10 - 0.30 |

## Configuration Presets

### Using Built-in Presets

```python
from groundcrew.config import (
    DEFAULT_CONFIG,       # Balanced
    HIGH_QUALITY_CONFIG,  # GPT-4, thorough search
    FAST_CONFIG          # GPT-4o-mini, quick
)

result = run_fact_check(
    input_text="...",
    model_name=HIGH_QUALITY_CONFIG.model_name
)
```

### Custom Configuration

```python
from groundcrew.config import GroundCrewConfig

config = GroundCrewConfig(
    model_name="gpt-4",
    temperature=0.0,
    max_search_results_per_query=5,
    max_queries_per_claim=3,
    search_depth="advanced"
)

result = run_fact_check(
    input_text="...",
    model_name=config.model_name
)
```

## Batch Processing

### Process Multiple Texts

```python
texts = [
    "Claim 1 to check",
    "Claim 2 to check",
    "Claim 3 to check"
]

for text in texts:
    result = run_fact_check(
        input_text=text,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        tavily_api_key=os.getenv("TAVILY_API_KEY")
    )
    print(f"\n{'='*70}")
    print(result.final_report)
```

### With Rate Limiting

```python
import time

for text in texts:
    result = run_fact_check(text, ...)
    print(result.final_report)
    time.sleep(2)  # Wait 2 seconds between requests
```

## Exporting Results

### JSON Export

```python
import json

result = run_fact_check(...)

# Export verdicts
data = {
    "claims": [c.dict() for c in result.claims],
    "verdicts": [v.dict() for v in result.verdicts],
    "report": result.final_report
}

with open("fact_check_results.json", "w") as f:
    json.dump(data, f, indent=2)
```

### CSV Export

```python
import csv

result = run_fact_check(...)

with open("verdicts.csv", "w") as f:
    writer = csv.DictWriter(
        f, 
        fieldnames=["claim", "status", "confidence", "justification"]
    )
    writer.writeheader()
    for v in result.verdicts:
        writer.writerow({
            "claim": v.claim,
            "status": v.status,
            "confidence": v.confidence,
            "justification": v.justification
        })
```

## Verdict Statuses

| Status | Meaning | Emoji |
|--------|---------|-------|
| `supported` | Evidence confirms the claim | ✅ |
| `refuted` | Evidence contradicts the claim | ❌ |
| `mixed` | Evidence both supports and refutes | ⚠️ |
| `not_enough_info` | Insufficient evidence found | ❓ |

## Best Practices

### 1. Claim Specificity
More specific claims produce better results:
- ✅ Good: "The Eiffel Tower is 330 meters tall"
- ❌ Poor: "The Eiffel Tower is big"

### 2. Model Selection
- Use `gpt-4o-mini` for most cases (fast, cheap, good quality)
- Use `gpt-4` for critical fact-checks requiring highest accuracy
- Start with cheaper models, upgrade if needed

### 3. Confidence Thresholds
- High confidence (>0.8): Likely accurate
- Medium confidence (0.5-0.8): Review recommended
- Low confidence (<0.5): Manual verification needed

### 4. Evidence Review
Always review the evidence sources:
```python
for verdict in result.verdicts:
    if verdict.confidence < 0.7:
        print(f"⚠️ Low confidence for: {verdict.claim}")
        for ev in verdict.evidence_used:
            print(f"  Check: {ev.source}")
```

### 5. Rate Limiting
Respect API rate limits:
- Add delays between batch requests
- Monitor your API usage
- Consider upgrading API tiers for heavy use

## Examples

See [Examples](Examples.md) for complete working examples including:
- Simple fact-checking
- Batch processing
- Custom configuration
- Integration examples

## Next Steps

- Learn about [Architecture](Architecture.md) to understand the pipeline
- See [API Reference](API-Reference.md) for detailed configuration options
- Check [Troubleshooting](Troubleshooting.md) if you encounter issues

