# Troubleshooting

Solutions to common issues and problems.

## Installation Issues

### Poetry Not Found

**Problem:** `poetry: command not found`

**Solution:**
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Add to PATH (Linux/Mac)
export PATH="$HOME/.local/bin:$PATH"

# Restart shell
exec $SHELL
```

### Dependency Installation Fails

**Problem:** `poetry install` fails with dependency conflicts

**Solution:**
```bash
# Clear cache
poetry cache clear --all pypi

# Remove lock file
rm poetry.lock

# Reinstall
poetry install
```

### Python Version Mismatch

**Problem:** `Requires python ^3.10 but 3.9 is installed`

**Solution:**
```bash
# Check Python version
python --version

# Use pyenv to install correct version
pyenv install 3.10.13
pyenv local 3.10.13

# Reinstall dependencies
poetry install
```

## API Key Issues

### API Key Not Found

**Problem:** `Error: OPENAI_API_KEY not found`

**Solutions:**

1. **Check `.env` file exists:**
```bash
ls -la .env
cat .env
```

2. **Create `.env` from template:**
```bash
cp env.template .env
# Edit .env with your keys
```

3. **Export directly:**
```bash
export OPENAI_API_KEY="sk-..."
export TAVILY_API_KEY="tvly-..."
```

4. **Check `.env` is loaded:**
```python
from dotenv import load_dotenv
import os

load_dotenv()
print(os.getenv("OPENAI_API_KEY"))  # Should not be None
```

### Invalid API Key

**Problem:** `AuthenticationError: Incorrect API key`

**Solution:**
- Verify key is correct (copy-paste carefully)
- Check for extra spaces or quotes
- Ensure key is active (not revoked)
- Test key directly: https://platform.openai.com/playground

### Rate Limit Exceeded

**Problem:** `RateLimitError: Rate limit reached`

**Solution:**
```python
import time

# Add delays between requests
for text in texts:
    result = run_fact_check(text, ...)
    time.sleep(2)  # Wait 2 seconds
```

Or upgrade your API plan.

## Runtime Issues

### Module Not Found

**Problem:** `ModuleNotFoundError: No module named 'groundcrew'`

**Solution:**
```bash
# Make sure you're in Poetry shell
poetry shell

# Or run with poetry prefix
poetry run python main.py

# Verify installation
poetry show | grep groundcrew
```

### Import Errors

**Problem:** `ImportError: cannot import name 'ClaimsList'`

**Solution:**
```bash
# Reinstall package
poetry install --no-root
poetry install
```

### Slow Performance

**Problem:** Fact-checking takes too long

**Solutions:**

1. **Use faster model:**
```python
model_name="gpt-4o-mini"  # Instead of gpt-4
```

2. **Reduce search depth:**
```python
from groundcrew.config import GroundCrewConfig

config = GroundCrewConfig(
    max_search_results_per_query=2,  # Instead of 3
    max_queries_per_claim=1,          # Instead of 2
    search_depth="basic"              # Instead of "advanced"
)
```

3. **Process fewer claims:**
- Use more specific input text
- Focus on key claims only

### Out of Memory

**Problem:** `MemoryError` or system freezes

**Solution:**
```python
# Process in smaller batches
batch_size = 5
for i in range(0, len(texts), batch_size):
    batch = texts[i:i+batch_size]
    for text in batch:
        result = run_fact_check(text, ...)
```

## Network Issues

### Connection Timeout

**Problem:** `ConnectionError: Connection timed out`

**Solutions:**

1. **Check internet connection**
2. **Verify API endpoints are accessible:**
```bash
curl https://api.openai.com
curl https://api.tavily.com
```

3. **Configure timeout:**
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    request_timeout=60  # Increase timeout
)
```

### SSL Certificate Error

**Problem:** `SSLError: certificate verify failed`

**Solution:**
```bash
# Update certificates (Mac)
/Applications/Python\ 3.10/Install\ Certificates.command

# Or set environment variable (temporary)
export PYTHONHTTPSVERIFY=0
```

## Validation Errors

### Pydantic Validation Error

**Problem:** `ValidationError: 1 validation error for VerdictOutput`

**This is normal** - it means LLM returned invalid data. The system has fallback behavior.

Check `result.error` for details:
```python
result = run_fact_check(...)
if result.error:
    print(f"Warning: {result.error}")
```

### Confidence Out of Bounds

**Problem:** LLM returns confidence > 1.0 or < 0.0

**Solution:** Pydantic automatically validates and rejects invalid values. The system uses fallback verdict.

## Output Issues

### Empty Results

**Problem:** No claims found or empty verdicts

**Possible causes:**

1. **Input too vague:**
```python
# Bad
input_text = "Things are big."

# Good
input_text = "The Eiffel Tower is 330 meters tall."
```

2. **Subjective input:**
```python
# Bad (opinion)
input_text = "The movie was great."

# Good (factual)
input_text = "The movie was released in 2023."
```

### Incorrect Verdicts

**Problem:** System gives wrong verdict

**Solutions:**

1. **Use better model:**
```python
model_name="gpt-4"  # More accurate than gpt-4o-mini
```

2. **Check evidence sources:**
```python
for verdict in result.verdicts:
    print(f"Claim: {verdict.claim}")
    for ev in verdict.evidence_used:
        print(f"  {ev.source}")
```

3. **Verify claim specificity:**
- More specific claims get better results
- Avoid ambiguous language

### Low Confidence Scores

**Problem:** All verdicts have low confidence (<0.5)

**Possible causes:**
- Not enough evidence found
- Contradictory evidence
- Claim too vague or complex

**Solution:**
```python
# Check evidence
for claim_text, evidence_list in result.evidence_map.items():
    print(f"{claim_text}: {len(evidence_list)} pieces of evidence")
    
    if len(evidence_list) == 0:
        print("  ⚠️ No evidence found!")
```

## Testing Issues

### Tests Fail

**Problem:** `pytest` tests fail

**Solution:**
```bash
# Run tests with verbose output
poetry run pytest -vv

# Run specific failing test
poetry run pytest tests/test_models.py::test_claim_creation -vv

# Check for dependency issues
poetry install
```

### Import Errors in Tests

**Problem:** `ModuleNotFoundError` during tests

**Solution:**
```bash
# Install package in editable mode
poetry install

# Run with poetry
poetry run pytest
```

## Performance Optimization

### Too Many API Calls

**Problem:** High API costs

**Solutions:**

1. **Cache results:**
```python
import json

# Save results
with open("results.json", "w") as f:
    json.dump(result.dict(), f)

# Load results
with open("results.json") as f:
    data = json.load(f)
```

2. **Batch similar claims:**
- Group related claims
- Process once, reuse evidence

3. **Use cheaper model:**
```python
model_name="gpt-4o-mini"  # Much cheaper than gpt-4
```

### Memory Usage

**Problem:** High memory consumption

**Solution:**
```python
# Clear large objects
del result
import gc
gc.collect()

# Process in batches
# Don't keep all results in memory
```

## Getting Help

### Check Documentation

1. [Getting Started](Getting-Started.md)
2. [Usage Guide](Usage-Guide.md)
3. [API Reference](API-Reference.md)
4. [Architecture](Architecture.md)

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)

result = run_fact_check(...)
```

### Create Issue

If problem persists:

1. Check existing issues on GitHub
2. Create new issue with:
   - Description of problem
   - Steps to reproduce
   - Error messages
   - System information (OS, Python version)
   - Minimal code example

### Community Support

- GitHub Discussions
- Stack Overflow (tag: groundcrew)

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `OPENAI_API_KEY not found` | Missing API key | Set in `.env` or export |
| `RateLimitError` | Too many requests | Add delays, upgrade plan |
| `ValidationError` | Invalid LLM output | Check `result.error`, normal |
| `ConnectionError` | Network issue | Check internet, firewall |
| `ModuleNotFoundError` | Package not installed | `poetry install` |
| `AuthenticationError` | Invalid API key | Verify key is correct |

## Still Having Issues?

Open an issue on GitHub with:
- Complete error message
- Your code (minimal reproducible example)
- Python version: `python --version`
- Package versions: `poetry show`
- Operating system

We're here to help! 🚀

