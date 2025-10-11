# API Reference

Complete reference for GroundCrew's API, models, and configuration.

## Main Function

### `run_fact_check()`

Run the complete fact-checking pipeline.

```python
def run_fact_check(
    input_text: str,
    openai_api_key: str,
    tavily_api_key: str,
    model_name: str = "gpt-4o-mini"
) -> FactCheckState
```

**Parameters:**
- `input_text` (str): Text to fact-check
- `openai_api_key` (str): OpenAI API key
- `tavily_api_key` (str): Tavily API key
- `model_name` (str, optional): OpenAI model to use. Default: `"gpt-4o-mini"`

**Returns:**
- `FactCheckState`: Complete state with all results

**Example:**
```python
from groundcrew.workflow import run_fact_check

result = run_fact_check(
    input_text="The Earth is round.",
    openai_api_key="sk-...",
    tavily_api_key="tvly-...",
    model_name="gpt-4o-mini"
)
```

## Data Models

### Claim

Represents a single factual claim.

```python
class Claim(BaseModel):
    text: str  # The claim text
    priority: int = 5  # Priority level (1-10, higher is more important)
```

**Example:**
```python
claim = Claim(
    text="The Eiffel Tower is 330 meters tall",
    priority=8
)
```

### ClaimsList

Container for multiple claims (used internally for structured output).

```python
class ClaimsList(BaseModel):
    claims: List[Claim]
```

### Evidence

Represents a piece of evidence from a source.

```python
class Evidence(BaseModel):
    source: str  # Source URL or reference
    snippet: str  # Relevant text snippet
    relevance_score: float = 0.0  # Relevance (0-1)
```

**Example:**
```python
evidence = Evidence(
    source="https://example.com/article",
    snippet="The Eiffel Tower stands at 330 meters...",
    relevance_score=0.95
)
```

### SearchQueries

Container for search queries (used internally for structured output).

```python
class SearchQueries(BaseModel):
    queries: List[str]  # List of 1-3 search queries
```

### VerdictOutput

LLM output for verification (used internally for structured output).

```python
class VerdictOutput(BaseModel):
    status: Literal["supported", "refuted", "mixed", "not_enough_info"]
    confidence: float  # Confidence level (0.0-1.0)
    justification: str  # Explanation
```

### Verdict

Complete verdict for a claim including evidence.

```python
class Verdict(BaseModel):
    claim: str  # The original claim
    status: Literal["supported", "refuted", "mixed", "not_enough_info"]
    confidence: float  # Confidence level (0-1)
    justification: str  # Explanation
    evidence_used: List[Evidence] = []  # Supporting evidence
```

**Example:**
```python
verdict = Verdict(
    claim="The Earth is round",
    status="supported",
    confidence=0.99,
    justification="Overwhelming evidence from multiple sources",
    evidence_used=[evidence1, evidence2]
)
```

### FactCheckState

Main state object that flows through the pipeline.

```python
class FactCheckState(BaseModel):
    # Input
    input_text: str
    
    # Stage outputs
    claims: List[Claim] = []
    evidence_map: Dict[str, List[Evidence]] = {}
    verdicts: List[Verdict] = []
    final_report: str = ""
    
    # Metadata
    error: str = ""
```

**Accessing Results:**
```python
result = run_fact_check(...)

# Original input
print(result.input_text)

# Extracted claims
for claim in result.claims:
    print(claim.text, claim.priority)

# Evidence for each claim
for claim_text, evidence_list in result.evidence_map.items():
    for evidence in evidence_list:
        print(evidence.source)

# Verdicts
for verdict in result.verdicts:
    print(verdict.claim, verdict.status, verdict.confidence)

# Final report
print(result.final_report)

# Any errors
if result.error:
    print(result.error)
```

## Configuration

### GroundCrewConfig

Configuration settings for the fact-checking workflow.

```python
class GroundCrewConfig(BaseModel):
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.0  # 0.0-2.0
    max_search_results_per_query: int = 3  # 1-10
    max_queries_per_claim: int = 2  # 1-5
    search_depth: Literal["basic", "advanced"] = "advanced"
    max_evidence_per_claim: int = 5  # 1-20
    snippet_max_length: int = 500  # 100-2000
    evidence_for_verdict: int = 3  # 1-10
    verbose: bool = True
```

**Example:**
```python
from groundcrew.config import GroundCrewConfig

config = GroundCrewConfig(
    model_name="gpt-4",
    temperature=0.0,
    max_search_results_per_query=5,
    max_queries_per_claim=3,
    search_depth="advanced",
    max_evidence_per_claim=10
)
```

### Built-in Presets

```python
from groundcrew.config import (
    DEFAULT_CONFIG,       # Balanced performance/quality
    HIGH_QUALITY_CONFIG,  # GPT-4, more thorough
    FAST_CONFIG          # GPT-4o-mini, quick
)
```

**DEFAULT_CONFIG:**
```python
GroundCrewConfig(
    model_name="gpt-4o-mini",
    max_search_results_per_query=3,
    max_queries_per_claim=2,
    search_depth="advanced"
)
```

**HIGH_QUALITY_CONFIG:**
```python
GroundCrewConfig(
    model_name="gpt-4",
    max_search_results_per_query=5,
    max_queries_per_claim=3,
    max_evidence_per_claim=10
)
```

**FAST_CONFIG:**
```python
GroundCrewConfig(
    model_name="gpt-4o-mini",
    max_search_results_per_query=2,
    max_queries_per_claim=1,
    search_depth="basic"
)
```

## Agents

### ClaimExtractionAgent

Extracts factual claims from text.

```python
class ClaimExtractionAgent:
    def __init__(self, llm: ChatOpenAI)
    def extract_claims(self, state: FactCheckState) -> FactCheckState
```

**Uses:** Structured output with `ClaimsList` model

### EvidenceSearchAgent

Retrieves evidence for claims.

```python
class EvidenceSearchAgent:
    def __init__(self, llm: ChatOpenAI, tavily_client: TavilyClient)
    def search_evidence(self, state: FactCheckState) -> FactCheckState
```

**Uses:** Structured output with `SearchQueries` model + Tavily API

### VerificationAgent

Verifies claims against evidence.

```python
class VerificationAgent:
    def __init__(self, llm: ChatOpenAI)
    def verify_claims(self, state: FactCheckState) -> FactCheckState
```

**Uses:** Structured output with `VerdictOutput` model

### ReportingAgent

Generates final report.

```python
class ReportingAgent:
    def __init__(self, llm: ChatOpenAI)
    def generate_report(self, state: FactCheckState) -> FactCheckState
```

**Uses:** Standard LLM text generation

## Supported Models

### OpenAI Models

- `gpt-4o-mini` - Fast, cost-effective (recommended)
- `gpt-4` - Highest quality
- `gpt-4-turbo` - Faster GPT-4
- `gpt-3.5-turbo` - Budget option (lower quality)

### Model Requirements

All models must support:
- Text generation
- Function calling (for structured output)
- System messages

## Error Handling

### Exception Types

GroundCrew uses standard Python exceptions:
- `ValueError`: Invalid parameters
- `KeyError`: Missing required fields
- `ConnectionError`: API connection issues
- `ValidationError`: Pydantic validation failures

### Error Tracking

Errors are tracked in `FactCheckState.error`:

```python
result = run_fact_check(...)

if result.error:
    print(f"Warning: {result.error}")
    # System continues with fallback behavior
```

## Rate Limits

### OpenAI
- Depends on your account tier
- Monitor usage at platform.openai.com

### Tavily
- Free tier: 1,000 requests/month
- Paid tiers available

### Best Practices

```python
import time

for text in texts:
    result = run_fact_check(text, ...)
    time.sleep(1)  # Add delay between requests
```

## Pydantic Validation

All models use Pydantic for validation:

```python
# Confidence must be 0.0-1.0
verdict = VerdictOutput(
    status="supported",
    confidence=0.95,  # ✅ Valid
    justification="..."
)

verdict = VerdictOutput(
    status="supported",
    confidence=1.5,  # ❌ ValidationError
    justification="..."
)
```

## Type Hints

GroundCrew is fully typed:

```python
from groundcrew.workflow import run_fact_check
from groundcrew.models import FactCheckState

result: FactCheckState = run_fact_check(...)
```

Use with mypy for type checking:
```bash
mypy groundcrew/
```

## Next Steps

- See [Usage Guide](Usage-Guide.md) for practical examples
- Read [Architecture](Architecture.md) to understand implementation
- Check [Examples](Examples.md) for code samples

