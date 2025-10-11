# Evaluation

Guide for evaluating GroundCrew's performance using benchmark datasets.

## FEVER Dataset Evaluation

GroundCrew can be evaluated against the [FEVER (Fact Extraction and VERification)](https://fever.ai) dataset, a standard benchmark for fact-checking systems.

### What is FEVER?

- **185,000+ claims** derived from Wikipedia
- **Three labels**: SUPPORTS, REFUTES, NOT ENOUGH INFO
- **Standard benchmark** for automated fact-checking research
- **Task**: Given a claim, retrieve evidence and classify its veracity

### Quick Start

```bash
# Evaluate on 100 samples (recommended for first run)
python eval_fever.py -n 100

# Evaluate on larger set
python eval_fever.py -n 500

# Custom output file
python eval_fever.py -n 100 -o my_results.json

# Analyze existing results
python eval_fever.py --analyze -o fever_evaluation_results.json
```

### Understanding Results

The evaluation produces:

#### 1. Overall Metrics
```
Overall Accuracy: 75.50% (151/200)
```

#### 2. Per-Label Performance
```
Per-Label Performance:
  SUPPORTS: 80.00% (64/80)
  REFUTES: 72.50% (58/80)  
  NOT ENOUGH INFO: 72.50% (29/40)
```

#### 3. Confidence Calibration
```
Confidence Calibration:
  high (>0.8): 85.00% (60 predictions)
  medium (0.5-0.8): 70.00% (80 predictions)
  low (<0.5): 55.00% (60 predictions)
```

Shows whether high-confidence predictions are actually more accurate.

#### 4. Individual Results
Detailed breakdown of each prediction for error analysis.

### Evaluation Metrics

| Metric | Description | Good Target |
|--------|-------------|-------------|
| **Overall Accuracy** | % of correct classifications | >70% |
| **Label Accuracy** | Accuracy per class (SUPPORTS/REFUTES/NEI) | Balanced across labels |
| **Confidence Calibration** | High confidence → higher accuracy | Strong correlation |

### Output Format

Results are saved as JSON:

```json
{
  "metadata": {
    "timestamp": "2025-10-11T...",
    "dataset": "FEVER",
    "num_samples": 100,
    "model": "gpt-4o-mini"
  },
  "overall_metrics": {
    "accuracy": 0.75,
    "correct": 75,
    "total": 100
  },
  "per_label_metrics": {
    "SUPPORTS": {"accuracy": 0.80, "correct": 32, "total": 40},
    ...
  },
  "confidence_calibration": {...},
  "individual_results": [
    {
      "claim": "...",
      "true_label": "SUPPORTS",
      "predicted_label": "SUPPORTS",
      "correct": true,
      "confidence": 0.95,
      "justification": "..."
    },
    ...
  ]
}
```

### Error Analysis

Use the analyze mode to understand failure patterns:

```bash
python eval_fever.py --analyze
```

Output shows:
- Error patterns (which label confusions are common)
- Example errors with confidence scores
- Helps identify systematic issues

### Important Differences

#### GroundCrew vs FEVER

| Aspect | GroundCrew | FEVER |
|--------|-----------|-------|
| Evidence Source | Live web (Tavily) | Wikipedia (static) |
| Claims | User-provided | Pre-labeled |
| Timeframe | Current information | Historical data |
| Coverage | Broad web | Wikipedia only |

**Why this matters:**

- FEVER evidence is from Wikipedia; GroundCrew searches the live web
- Some claims may have different verdicts based on evidence source
- Recent events may have more/better evidence on web vs Wikipedia
- Wikipedia-specific claims may be harder for web search

### Expected Performance

Based on the differences:

- **60-75%** accuracy is reasonable for web search vs Wikipedia evidence
- **Higher accuracy** on general knowledge claims
- **Lower accuracy** on Wikipedia-specific or historical claims
- **Mixed** labels may differ due to evidence source diversity

### Recommendations

#### For Better Results:

1. **Use GPT-4** instead of GPT-4o-mini:
```bash
# Edit eval_fever.py, line with model_name
model_name="gpt-4"
```

2. **Adjust evidence threshold** in agents.py to require more evidence

3. **Test on multiple splits**:
```bash
python eval_fever.py --split validation -n 100
python eval_fever.py --split train -n 100
```

#### Interpreting Results:

- **High accuracy (>80%)**: System works well for this claim type
- **Low confidence correlation**: System may be over/under confident
- **Label imbalance**: Check if one label dominates errors

### Common Issues

#### Low Accuracy (<60%)

Possible causes:
- Evidence source mismatch (web vs Wikipedia)
- Model not powerful enough (try GPT-4)
- Claims require domain expertise
- Evidence retrieval not finding relevant sources

#### Accuracy Good But Confidence Poor

Possible causes:
- LLM over-confident on uncertain claims
- Need confidence calibration
- Mixed evidence not handled well

#### High Cost

- Reduce num_samples: `-n 50`
- Use gpt-4o-mini (cheaper but less accurate)
- Cache results and analyze patterns

### Sample Size Recommendations

| Purpose | Samples | Time | Cost (approx) |
|---------|---------|------|---------------|
| Quick test | 50 | ~15 min | $2-5 |
| Standard eval | 100 | ~30 min | $5-10 |
| Thorough eval | 200-500 | 1-3 hours | $20-50 |

Cost assumes gpt-4o-mini. GPT-4 is 10x more expensive.

### Custom Evaluation

For domain-specific evaluation, create your own test set:

```python
custom_claims = [
    {
        "claim": "Your domain-specific claim",
        "expected_label": "SUPPORTS",
        "notes": "Why this is important"
    },
    # ... more claims
]

# Run GroundCrew on each
for item in custom_claims:
    result = run_fact_check(item["claim"], ...)
    # Compare and analyze
```

### Continuous Evaluation

For production use:

1. **Baseline**: Run eval_fever.py monthly
2. **Track metrics** over time
3. **A/B test** changes (different models, prompts)
4. **Monitor** confidence calibration
5. **Review** systematic errors

### Alternative Datasets

Other datasets to consider:

- **LIAR**: Political claims (PolitiFact)
- **CLIMATE-FEVER**: Climate science claims
- **MultiFC**: Multi-domain claims
- **FEVEROUS**: Structured evidence (tables + text)

Each requires a different evaluation script but follows similar patterns.

### Next Steps

- See [Development Guide](Development.md) for improving the system
- Check [Troubleshooting](Troubleshooting.md) for common issues
- Read [Architecture](Architecture.md) to understand system design

## Cost Estimation

Before running evaluation:

```python
# Rough cost estimate
num_samples = 100
cost_per_check = 0.05  # For gpt-4o-mini
total_cost = num_samples * cost_per_check

print(f"Estimated cost: ${total_cost:.2f}")
# ~$5 for 100 samples with gpt-4o-mini
# ~$50 for 100 samples with gpt-4
```

## References

- FEVER Dataset: https://fever.ai
- Paper: "FEVER: a large-scale dataset for Fact Extraction and VERification"
- Leaderboard: https://fever.ai/leaderboard.html

