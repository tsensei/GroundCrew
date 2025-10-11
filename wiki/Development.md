# Development Guide

Guide for contributing to and extending GroundCrew.

## Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/yourusername/GroundCrew.git
cd GroundCrew
```

### 2. Install Dependencies

```bash
poetry install
```

### 3. Run Tests

```bash
poetry run pytest tests/ -v
```

All tests should pass before making changes.

## Project Structure

```
GroundCrew/
├── groundcrew/           # Main package
│   ├── __init__.py       # Package initialization
│   ├── models.py         # Pydantic data models
│   ├── agents.py         # Agent implementations
│   ├── workflow.py       # LangGraph workflow
│   └── config.py         # Configuration settings
├── tests/                # Test suite
│   ├── __init__.py
│   ├── test_models.py    # Model tests
│   └── test_imports.py   # Import tests
├── examples/             # Example scripts
│   ├── simple_check.py
│   ├── advanced_config.py
│   └── batch_check.py
├── wiki/                 # Documentation
├── main.py               # CLI entry point
├── demo.py               # Interactive demo
└── setup.sh              # Setup script
```

## Code Style

### Formatting

We use **Black** for code formatting:

```bash
poetry run black groundcrew/ tests/
```

### Linting

We use **Ruff** for linting:

```bash
poetry run ruff check groundcrew/ tests/
```

### Type Hints

Always use type hints:

```python
def process_claim(claim: Claim) -> Verdict:
    # Implementation
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def extract_claims(text: str) -> List[Claim]:
    """Extract factual claims from text.
    
    Args:
        text: Input text to analyze
        
    Returns:
        List of extracted claims
    """
    pass
```

## Testing

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=groundcrew

# Run specific test file
poetry run pytest tests/test_models.py -v

# Run specific test
poetry run pytest tests/test_models.py::test_claim_creation
```

### Writing Tests

Place tests in `tests/` directory:

```python
def test_claim_extraction():
    """Test that claims are extracted correctly."""
    # Arrange
    text = "The Earth is round."
    
    # Act
    claims = extract_claims(text)
    
    # Assert
    assert len(claims) > 0
    assert "Earth" in claims[0].text
```

### Test Naming

- Test files: `test_*.py`
- Test functions: `test_*`
- Use descriptive names
- One assertion per test (when possible)

## Adding Features

### Adding a New Agent

1. **Define Output Model** (`models.py`):

```python
class MyAgentOutput(BaseModel):
    result: str
    confidence: float
```

2. **Create Agent Class** (`agents.py`):

```python
class MyNewAgent:
    def __init__(self, llm: ChatOpenAI):
        self.structured_llm = llm.with_structured_output(MyAgentOutput)
    
    def process(self, state: FactCheckState) -> FactCheckState:
        output: MyAgentOutput = self.structured_llm.invoke(prompt)
        # Update state
        return state
```

3. **Add to Workflow** (`workflow.py`):

```python
def my_new_node(state: dict) -> dict:
    agent = MyNewAgent(llm)
    updated_state = agent.process(state["state"])
    return {"state": updated_state}

workflow.add_node("my_new_stage", my_new_node)
workflow.add_edge("previous_stage", "my_new_stage")
workflow.add_edge("my_new_stage", "next_stage")
```

4. **Add Tests** (`tests/test_agents.py`):

```python
def test_my_new_agent():
    """Test MyNewAgent processes state correctly."""
    # Test implementation
    pass
```

### Adding Configuration Options

Update `config.py`:

```python
class GroundCrewConfig(BaseModel):
    my_new_setting: int = Field(
        default=10,
        description="Description of the setting",
        ge=1,
        le=100
    )
```

### Adding Examples

Create example in `examples/`:

```python
"""Example: Custom configuration"""

from groundcrew.workflow import run_fact_check
from groundcrew.config import GroundCrewConfig

config = GroundCrewConfig(...)
result = run_fact_check(...)
```

## Pull Request Process

### 1. Create Branch

```bash
git checkout -b feature/my-new-feature
```

### 2. Make Changes

- Write clean, documented code
- Add tests for new functionality
- Update documentation if needed

### 3. Run Quality Checks

```bash
# Format code
poetry run black groundcrew/ tests/

# Lint
poetry run ruff check groundcrew/ tests/

# Run tests
poetry run pytest

# Check types (optional)
mypy groundcrew/
```

### 4. Commit

Use conventional commits:

```bash
git commit -m "Add: new verification agent for images"
git commit -m "Fix: claim extraction edge case"
git commit -m "Docs: update architecture guide"
git commit -m "Test: add tests for batch processing"
```

Prefixes:
- `Add:` - New features
- `Fix:` - Bug fixes
- `Docs:` - Documentation
- `Test:` - Tests
- `Refactor:` - Code refactoring
- `Chore:` - Maintenance tasks

### 5. Push and Create PR

```bash
git push origin feature/my-new-feature
```

Create Pull Request on GitHub with:
- Clear description of changes
- Reference to related issues
- Screenshots/examples if applicable

## Code Review

All PRs require:
- ✅ Passing tests
- ✅ Code review approval
- ✅ No linter errors
- ✅ Updated documentation
- ✅ No merge conflicts

## Areas for Contribution

### High Priority

- [ ] Web UI for easier interaction
- [ ] Support for multiple languages
- [ ] Integration with fact-check databases
- [ ] Caching layer for evidence
- [ ] Batch processing optimizations

### Medium Priority

- [ ] Visual evidence analysis (images, charts)
- [ ] Custom evidence source plugins
- [ ] Export to different formats (PDF, markdown)
- [ ] Confidence calibration
- [ ] Human-in-the-loop review

### Documentation

- [ ] More examples
- [ ] Video tutorials
- [ ] API documentation site
- [ ] Architecture diagrams
- [ ] Performance benchmarks

### Testing

- [ ] Integration tests with real APIs
- [ ] Performance tests
- [ ] Edge case testing
- [ ] Mock API responses

## Dependency Management

### Adding Dependencies

```bash
# Runtime dependency
poetry add package-name

# Dev dependency
poetry add --group dev package-name
```

### Updating Dependencies

```bash
# Update all
poetry update

# Update specific package
poetry update package-name
```

### Check for Updates

```bash
poetry show --outdated
```

## Release Process

### Version Numbering

We use semantic versioning: `MAJOR.MINOR.PATCH`

- `MAJOR`: Breaking changes
- `MINOR`: New features (backward compatible)
- `PATCH`: Bug fixes

### Creating a Release

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create git tag
4. Push to GitHub
5. Create GitHub release

## Debugging

### Enable Verbose Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Inspect State

```python
result = run_fact_check(...)

print(f"Claims: {len(result.claims)}")
print(f"Evidence: {len(result.evidence_map)}")
print(f"Verdicts: {len(result.verdicts)}")

if result.error:
    print(f"Error: {result.error}")
```

### Test Individual Agents

```python
from groundcrew.agents import ClaimExtractionAgent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(api_key="...", model="gpt-4o-mini")
agent = ClaimExtractionAgent(llm)

state = FactCheckState(input_text="Test text")
result = agent.extract_claims(state)
print(result.claims)
```

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Check existing issues before creating new ones

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Next Steps

- Read [Architecture](Architecture.md) to understand the system
- Check [API Reference](API-Reference.md) for detailed documentation
- See [Examples](Examples.md) for code samples

