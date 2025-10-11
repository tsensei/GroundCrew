# Examples

Practical code examples for using GroundCrew.

## Basic Examples

### Simple Fact-Check

Check a single claim:

```python
from groundcrew.workflow import run_fact_check
import os

result = run_fact_check(
    input_text="The Eiffel Tower is 330 meters tall.",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    tavily_api_key=os.getenv("TAVILY_API_KEY")
)

print(result.final_report)
```

### Multiple Claims

Check text with multiple claims:

```python
text = """
The COVID-19 vaccine was developed in record time. Clinical trials 
showed the Pfizer vaccine was 95% effective. Over 600 million doses 
have been administered in the United States.
"""

result = run_fact_check(
    input_text=text.strip(),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    tavily_api_key=os.getenv("TAVILY_API_KEY")
)

# Access individual verdicts
for i, verdict in enumerate(result.verdicts, 1):
    print(f"\n[Claim {i}] {verdict.claim}")
    print(f"Status: {verdict.status.upper()}")
    print(f"Confidence: {verdict.confidence:.0%}")
    print(f"Justification: {verdict.justification}")
```

## Configuration Examples

### Using High Quality Config

```python
from groundcrew.workflow import run_fact_check
from groundcrew.config import HIGH_QUALITY_CONFIG
import os

result = run_fact_check(
    input_text="Complex claim requiring detailed verification",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    tavily_api_key=os.getenv("TAVILY_API_KEY"),
    model_name=HIGH_QUALITY_CONFIG.model_name  # Uses GPT-4
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
    search_depth="advanced",
    max_evidence_per_claim=10
)

result = run_fact_check(
    input_text="Your text",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    tavily_api_key=os.getenv("TAVILY_API_KEY"),
    model_name=config.model_name
)
```

### Fast Mode

```python
from groundcrew.config import FAST_CONFIG

result = run_fact_check(
    input_text="Quick check needed",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    tavily_api_key=os.getenv("TAVILY_API_KEY"),
    model_name=FAST_CONFIG.model_name
)
```

## Batch Processing

### Process Multiple Texts

```python
texts = [
    "The Earth orbits the Sun.",
    "Water boils at 100°C at sea level.",
    "The Great Wall of China is visible from space."
]

results = []
for text in texts:
    result = run_fact_check(
        input_text=text,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        tavily_api_key=os.getenv("TAVILY_API_KEY")
    )
    results.append(result)

# Print summary
for i, result in enumerate(results, 1):
    print(f"\n{'='*70}")
    print(f"Text {i}: {result.input_text[:50]}...")
    print(f"Claims found: {len(result.claims)}")
    print(f"Overall verdict: {result.verdicts[0].status if result.verdicts else 'N/A'}")
```

### With Progress Tracking

```python
from tqdm import tqdm
import time

texts = ["claim 1", "claim 2", "claim 3", ...]

results = []
for text in tqdm(texts, desc="Fact-checking"):
    result = run_fact_check(
        input_text=text,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        tavily_api_key=os.getenv("TAVILY_API_KEY")
    )
    results.append(result)
    time.sleep(1)  # Rate limiting
```

## Export Examples

### Export to JSON

```python
import json
from datetime import datetime

result = run_fact_check(...)

# Create structured output
output = {
    "timestamp": datetime.now().isoformat(),
    "input_text": result.input_text,
    "claims": [c.dict() for c in result.claims],
    "verdicts": [v.dict() for v in result.verdicts],
    "final_report": result.final_report
}

# Save to file
with open("fact_check_results.json", "w") as f:
    json.dump(output, f, indent=2)
```

### Export to CSV

```python
import csv

result = run_fact_check(...)

with open("verdicts.csv", "w", newline="") as f:
    writer = csv.writer(f)
    
    # Header
    writer.writerow(["Claim", "Status", "Confidence", "Justification"])
    
    # Data
    for v in result.verdicts:
        writer.writerow([
            v.claim,
            v.status,
            f"{v.confidence:.2f}",
            v.justification
        ])
```

### Export to Markdown

```python
result = run_fact_check(...)

markdown = f"""# Fact-Check Report

## Input
{result.input_text}

## Claims Analyzed
{len(result.claims)} claims found

## Verdicts

"""

for i, verdict in enumerate(result.verdicts, 1):
    status_emoji = {
            "SUPPORTS": "✅",
            "REFUTES": "❌",
            "NOT ENOUGH INFO": "❓"
    }.get(verdict.status, "•")
    
    markdown += f"""
### {i}. {verdict.claim}

**Status:** {status_emoji} {verdict.status.upper()}  
**Confidence:** {verdict.confidence:.0%}  
**Justification:** {verdict.justification}

"""

with open("report.md", "w") as f:
    f.write(markdown)
```

## Advanced Examples

### Filter by Confidence

```python
result = run_fact_check(...)

# Only show high confidence verdicts
high_confidence = [v for v in result.verdicts if v.confidence > 0.8]

for verdict in high_confidence:
    print(f"✅ {verdict.claim}: {verdict.status}")

# Flag low confidence for review
low_confidence = [v for v in result.verdicts if v.confidence < 0.5]

if low_confidence:
    print("\n⚠️ The following claims need manual review:")
    for verdict in low_confidence:
        print(f"  - {verdict.claim}")
```

### Custom Evidence Analysis

```python
result = run_fact_check(...)

# Analyze evidence sources
for claim_text, evidence_list in result.evidence_map.items():
    print(f"\nClaim: {claim_text}")
    print(f"Evidence sources: {len(evidence_list)}")
    
    # Group by domain
    domains = {}
    for ev in evidence_list:
        from urllib.parse import urlparse
        domain = urlparse(ev.source).netloc
        domains[domain] = domains.get(domain, 0) + 1
    
    print("Domains:")
    for domain, count in domains.items():
        print(f"  {domain}: {count}")
```

### Compare Multiple Models

```python
text = "Your claim to check"

models = ["gpt-4o-mini", "gpt-4"]
results = {}

for model in models:
    result = run_fact_check(
        input_text=text,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        tavily_api_key=os.getenv("TAVILY_API_KEY"),
        model_name=model
    )
    results[model] = result

# Compare
print(f"{'Model':<15} {'Claims':<10} {'Verdict':<20} {'Confidence'}")
print("="*60)

for model, result in results.items():
    if result.verdicts:
        v = result.verdicts[0]
        print(f"{model:<15} {len(result.claims):<10} {v.status:<20} {v.confidence:.0%}")
```

## Integration Examples

### Flask Web API

```python
from flask import Flask, request, jsonify
from groundcrew.workflow import run_fact_check
import os

app = Flask(__name__)

@app.route('/fact-check', methods=['POST'])
def fact_check():
    data = request.json
    text = data.get('text')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    result = run_fact_check(
        input_text=text,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        tavily_api_key=os.getenv("TAVILY_API_KEY")
    )
    
    return jsonify({
        "claims": len(result.claims),
        "verdicts": [v.dict() for v in result.verdicts],
        "report": result.final_report
    })

if __name__ == '__main__':
    app.run(debug=True)
```

### Streamlit UI

```python
import streamlit as st
from groundcrew.workflow import run_fact_check
import os

st.title("GroundCrew Fact-Checker")

text = st.text_area("Enter text to fact-check:", height=200)

if st.button("Check Facts"):
    if text:
        with st.spinner("Fact-checking..."):
            result = run_fact_check(
                input_text=text,
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                tavily_api_key=os.getenv("TAVILY_API_KEY")
            )
        
        st.success(f"Found {len(result.claims)} claims")
        
        for i, verdict in enumerate(result.verdicts, 1):
            with st.expander(f"Claim {i}: {verdict.claim}"):
                st.write(f"**Status:** {verdict.status}")
                st.write(f"**Confidence:** {verdict.confidence:.0%}")
                st.write(f"**Justification:** {verdict.justification}")
                
                if verdict.evidence_used:
                    st.write("**Evidence:**")
                    for ev in verdict.evidence_used:
                        st.write(f"- [{ev.source}]({ev.source})")
    else:
        st.warning("Please enter some text")
```

### Discord Bot

```python
import discord
from groundcrew.workflow import run_fact_check
import os

client = discord.Client()

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('!factcheck'):
        text = message.content[11:].strip()
        
        if not text:
            await message.channel.send("Usage: !factcheck <text>")
            return
        
        await message.channel.send("🔍 Fact-checking...")
        
        result = run_fact_check(
            input_text=text,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            tavily_api_key=os.getenv("TAVILY_API_KEY")
        )
        
        response = f"**Fact-Check Results**\n\n"
        for v in result.verdicts[:3]:  # Limit to 3
            status_emoji = {
            "SUPPORTS": "✅",
            "REFUTES": "❌",
            "NOT ENOUGH INFO": "❓"
            }.get(v.status, "•")
            
            response += f"{status_emoji} {v.claim}\n"
            response += f"Status: {v.status} ({v.confidence:.0%})\n\n"
        
        await message.channel.send(response)

client.run(os.getenv('DISCORD_TOKEN'))
```

## Testing Examples

### Unit Test

```python
def test_fact_check_basic():
    """Test basic fact-checking functionality."""
    result = run_fact_check(
        input_text="The Earth is round.",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        tavily_api_key=os.getenv("TAVILY_API_KEY")
    )
    
    assert len(result.claims) > 0
    assert len(result.verdicts) > 0
    assert result.final_report != ""
```

### Mock Test

```python
from unittest.mock import Mock, patch

def test_claim_extraction():
    """Test claim extraction with mocked LLM."""
    mock_llm = Mock()
    
    with patch('groundcrew.agents.ChatOpenAI', return_value=mock_llm):
        agent = ClaimExtractionAgent(mock_llm)
        # Test logic
```

## Next Steps

- See [Usage Guide](Usage-Guide.md) for detailed usage patterns
- Check [API Reference](API-Reference.md) for all available options
- Read [Architecture](Architecture.md) to understand the system
- Visit [Development](Development.md) to extend GroundCrew

