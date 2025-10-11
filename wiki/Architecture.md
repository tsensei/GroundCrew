# Architecture

Technical overview of GroundCrew's design and implementation.

## System Overview

GroundCrew implements a **sequential multi-agent pipeline** using LangGraph for workflow orchestration. The system processes input text through four distinct stages, each handled by a specialized agent.

```
┌──────────────────────────────────────────────────────────────┐
│                        INPUT TEXT                             │
└────────────────────────────┬─────────────────────────────────┘
                             ↓
┌────────────────────────────────────────────────────────────────┐
│  STAGE 1: Claim Extraction Agent                              │
│  • Analyzes input text with LLM                               │
│  • Identifies factual claims                                  │
│  • Filters out opinions/questions                             │
│  • Assigns priority scores (1-10)                             │
│  Output: List[Claim]                                          │
└────────────────────────────┬─────────────────────────────────┘
                             ↓
┌────────────────────────────────────────────────────────────────┐
│  STAGE 2: Evidence Search Agent                               │
│  • Generates search queries with LLM                          │
│  • Searches web via Tavily API                                │
│  • Collects relevant snippets                                 │
│  • Ranks evidence by relevance                                │
│  Output: Dict[Claim → List[Evidence]]                         │
└────────────────────────────┬─────────────────────────────────┘
                             ↓
┌────────────────────────────────────────────────────────────────┐
│  STAGE 3: Verification Agent                                  │
│  • Analyzes claim vs evidence with LLM                        │
│  • Determines verdict (supported/refuted/mixed/not_enough)    │
│  • Assigns confidence score (0-1)                             │
│  • Generates justification                                    │
│  Output: List[Verdict]                                        │
└────────────────────────────┬─────────────────────────────────┘
                             ↓
┌────────────────────────────────────────────────────────────────┐
│  STAGE 4: Reporting Agent                                     │
│  • Synthesizes all findings with LLM                          │
│  • Creates human-readable report                              │
│  • Formats verdicts and evidence                              │
│  • Generates summary                                          │
│  Output: Final Report (string)                                │
└────────────────────────────┬─────────────────────────────────┘
                             ↓
                      ┌──────────────┐
                      │ FINAL OUTPUT │
                      └──────────────┘
```

## Data Flow

### State Object

The pipeline uses a single `FactCheckState` object that flows through all stages:

```python
class FactCheckState(BaseModel):
    input_text: str                          # Original text
    claims: List[Claim]                      # Stage 1 output
    evidence_map: Dict[str, List[Evidence]]  # Stage 2 output
    verdicts: List[Verdict]                  # Stage 3 output
    final_report: str                        # Stage 4 output
    error: str                               # Error tracking
```

### Sequential Processing

```
State[input_text] 
  → ClaimAgent 
  → State[input_text, claims]
  → EvidenceAgent 
  → State[claims, evidence_map]
  → VerificationAgent 
  → State[verdicts]
  → ReportingAgent 
  → State[final_report]
```

Each agent receives the state, processes it, and returns an updated state.

## Agents

### 1. Claim Extraction Agent

**Purpose**: Identify check-worthy factual claims

**Implementation**:
- Uses LLM with structured output
- Returns `ClaimsList` Pydantic model
- Prioritizes claims by importance (1-10)
- Filters subjective statements

**Input Example**:
```
"The Eiffel Tower is 330m tall and was completed in 1889."
```

**Output Example**:
```python
ClaimsList(claims=[
    Claim(text="The Eiffel Tower is 330 meters tall", priority=7),
    Claim(text="The Eiffel Tower was completed in 1889", priority=8)
])
```

### 2. Evidence Search Agent

**Purpose**: Retrieve supporting/refuting evidence

**Implementation**:
- Generates 1-3 search queries per claim using LLM
- Returns `SearchQueries` Pydantic model
- Searches via Tavily API (advanced web search)
- Collects snippets with source URLs
- Ranks by relevance score

**Process**:
1. LLM generates search queries for claim
2. Each query sent to Tavily API
3. Top 3-5 results per query collected
4. Evidence stored in `evidence_map`

### 3. Verification Agent

**Purpose**: Determine claim truthfulness

**Implementation**:
- Analyzes claim against collected evidence using LLM
- Returns `VerdictOutput` Pydantic model
- Determines verdict: `supported`, `refuted`, `mixed`, or `not_enough_info`
- Assigns confidence score (0.0-1.0)
- Generates detailed justification

**Verdict Logic**:
- **Supported**: Evidence consistently confirms the claim
- **Refuted**: Evidence consistently contradicts the claim
- **Mixed**: Evidence both supports and contradicts
- **Not Enough Info**: Insufficient or unclear evidence

### 4. Reporting Agent

**Purpose**: Generate human-readable output

**Implementation**:
- Synthesizes all verdicts using LLM
- Creates structured report
- Includes claim-by-claim analysis
- Provides overall summary
- Formats for readability

## Structured Output

All agents use LangChain's `.with_structured_output()` method to guarantee type-safe, validated responses.

### How It Works

```python
class ClaimExtractionAgent:
    def __init__(self, llm: ChatOpenAI):
        # Create structured LLM
        self.structured_llm = llm.with_structured_output(ClaimsList)
    
    def extract_claims(self, state):
        # Invoke returns validated Pydantic model
        result: ClaimsList = self.structured_llm.invoke(prompt)
        return result.claims
```

### Benefits

- **Type Safety**: Full Pydantic validation
- **Reliability**: No JSON parsing errors
- **Clean Code**: No try/except for parsing
- **Better Errors**: Pydantic provides clear error messages

### Under the Hood

When you call `.with_structured_output(PydanticModel)`:

1. Converts Pydantic model to JSON schema
2. Uses OpenAI function calling API
3. Forces model to return structured data
4. Validates and parses into Pydantic model
5. Returns typed object

## LangGraph Integration

### Workflow Definition

```python
workflow = StateGraph(dict)

# Add nodes (agents)
workflow.add_node("extract_claims", extract_claims_node)
workflow.add_node("search_evidence", search_evidence_node)
workflow.add_node("verify_claims", verify_claims_node)
workflow.add_node("generate_report", generate_report_node)

# Define sequential flow
workflow.set_entry_point("extract_claims")
workflow.add_edge("extract_claims", "search_evidence")
workflow.add_edge("search_evidence", "verify_claims")
workflow.add_edge("verify_claims", "generate_report")
workflow.add_edge("generate_report", END)

# Compile
app = workflow.compile()
```

### Why LangGraph?

1. **State Management**: Automatic state passing between nodes
2. **Type Safety**: Typed state ensures data consistency
3. **Debugging**: Built-in visualization and logging
4. **Flexibility**: Easy to add conditional logic
5. **Scalability**: Can extend to complex workflows

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Orchestration | LangGraph | Workflow management |
| LLM Framework | LangChain | Agent abstractions |
| Language Model | OpenAI GPT | Reasoning & generation |
| Search API | Tavily | Evidence retrieval |
| Data Validation | Pydantic | Type safety |
| Package Management | Poetry | Dependencies |

## Design Decisions

### Sequential vs. Parallel

**Choice**: Sequential pipeline

**Rationale**:
- Each stage depends on previous output
- Claims must be extracted before searching
- Evidence must be gathered before verification
- Clear debugging and error tracking
- Simpler to understand and maintain

### Structured Output

**Choice**: Use `.with_structured_output()` for all LLM interactions

**Rationale**:
- Eliminates JSON parsing errors
- Provides type safety
- Cleaner code (no manual parsing)
- Better error messages
- Uses OpenAI function calling (more reliable)

### State Management

**Choice**: Immutable state object

**Rationale**:
- Functional programming principles
- Thread-safe
- Easy to serialize/deserialize
- Better for debugging and logging
- Clear data flow

## Performance

### Bottlenecks

1. **LLM Calls**: 4-5 calls per claim
2. **Search API**: Multiple web searches
3. **Network Latency**: External API dependencies

### Optimization Strategies

1. **Model Selection**: Use gpt-4o-mini for speed
2. **Reduce Search**: Limit queries per claim
3. **Batch Processing**: Group similar claims
4. **Caching**: Cache search results (future)
5. **Parallel Search**: Execute searches concurrently (future)

## Error Handling

### Graceful Degradation

- Claim extraction fails → treat input as single claim
- Search fails → proceed with partial evidence
- Verification fails → return "not_enough_info"
- Errors tracked in `state.error` field

### Validation

- Pydantic validates all structured outputs
- Confidence scores bounded to [0.0, 1.0]
- Status limited to valid literal values
- Type checking throughout

## Extensibility

### Adding New Agents

1. Create agent class in `groundcrew/agents.py`
2. Define Pydantic model for output
3. Use `.with_structured_output(YourModel)`
4. Add node to workflow in `groundcrew/workflow.py`
5. Update edges
6. Extend `FactCheckState` if needed

### Custom Evidence Sources

```python
class CustomSearchAgent:
    def search(self, claim):
        # Query scientific databases, APIs, etc.
        return evidence_list
```

### Parallel Processing

```python
# Process multiple claims in parallel
workflow.add_node("verify_claim_1", verify_node)
workflow.add_node("verify_claim_2", verify_node)
```

## Security & Privacy

- API keys stored in `.env` (gitignored)
- No data persistence by default
- All processing via OpenAI and Tavily APIs
- Review their privacy policies for details

## Next Steps

- See [API Reference](API-Reference.md) for detailed model documentation
- Check [Development](Development.md) for extending the system
- Read [Usage Guide](Usage-Guide.md) for practical examples

