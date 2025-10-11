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
# Uses 10 parallel workers by default for faster evaluation
poetry run python evals/eval_fever.py -n 100

# Evaluate with Wikipedia-only (recommended for FEVER accuracy)
poetry run python evals/eval_fever.py -n 100 --wikipedia-only -o evals/fever_wiki_results.json

# Evaluate on larger set
poetry run python evals/eval_fever.py -n 500 --wikipedia-only

# Custom output file and number of workers
poetry run python evals/eval_fever.py -n 100 -o evals/my_results.json -w 20

# Reduce workers if hitting rate limits
poetry run python evals/eval_fever.py -n 100 -w 5

# Analyze existing results
poetry run python evals/eval_fever.py --analyze -o evals/fever_evaluation_results.json
```

### Parallel Processing

The evaluation script uses **parallel processing** with ThreadPoolExecutor for much faster evaluation:

- **Default**: 10 parallel workers
- **Speed**: ~10x faster than sequential processing
- **Configurable**: Use `-w` or `--workers` to adjust

**Example performance:**
- Sequential: 20s per claim = 33+ minutes for 100 claims
- Parallel (10 workers): ~2-4 minutes for 100 claims ⚡

**Adjust workers based on:**
- **API rate limits**: Reduce workers (5-10) if hitting limits
- **Speed needs**: Increase workers (15-20) for faster evaluation
- **Cost**: More workers = faster but higher parallel API costs

### Understanding Results

The evaluation produces:

#### 1. Overall Metrics

**Actual GroundCrew Performance (100 samples, GPT-4o):**

| Configuration | Overall Accuracy | SUPPORTS | REFUTES | NOT ENOUGH INFO |
|---------------|------------------|----------|---------|-----------------|
| **Web Search** | 71% | 88% | 82% | 42% |
| **Wikipedia-only** | 72% | 91% | 88% | 36% |

#### 2. Per-Label Performance

**Web Search (Baseline):**
```
Overall Accuracy: 71% (71/100)
Per-Label:
  SUPPORTS: 88.2% (30/34)
  REFUTES: 81.8% (27/33)
  NOT ENOUGH INFO: 42.4% (14/33)
```

**Wikipedia-only (FEVER-aligned):**
```
Overall Accuracy: 72% (72/100)
Per-Label:
  SUPPORTS: 91.2% (31/34)
  REFUTES: 87.9% (29/33)
  NOT ENOUGH INFO: 36.4% (12/33)
```

#### 3. Key Findings

- ✅ **Strong on SUPPORTS/REFUTES**: 82-91% accuracy
- ⚠️ **Weak on NOT ENOUGH INFO**: 36-42% accuracy
- 📊 **Overall**: 71-72% competitive for web-based system
- 🔍 **Wikipedia-only**: Slightly better overall, but worse on NOT ENOUGH INFO (unexpected)

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

### Actual vs Expected Performance

**Our Results:**
- **71-72%** overall accuracy ✅ (better than expected!)
- **88-91%** on SUPPORTS ✅ (excellent)
- **82-88%** on REFUTES ✅ (excellent)  
- **36-42%** on NOT ENOUGH INFO ⚠️ (needs improvement)

**Comparison to FEVER Leaderboard:**
- Top systems: 85-90% (with Wikipedia access)
- Our system: 72% (web search or Wikipedia)
- **Competitive** considering we use LLM-based approach vs specialized models

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

**With Parallel Processing (10 workers):**

| Purpose | Samples | Time | Cost (approx) |
|---------|---------|------|---------------|
| Quick test | 50 | ~2-3 min | $2-5 |
| Standard eval | 100 | ~3-5 min | $5-10 |
| Thorough eval | 200-500 | ~10-25 min | $20-50 |

Cost assumes gpt-4o-mini. GPT-4 is 10x more expensive.

**Note**: Times are approximate with 10 parallel workers. Actual time depends on API response times and rate limits.

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

## NOT ENOUGH INFO Challenge

**Why This Label Is Hard:**

Our system struggles with NOT ENOUGH INFO (36-42% vs 88-91% on other labels):

1. **Over-confident predictions**: LLM makes judgments on partial evidence
2. **Evidence source**: We find related info, but it doesn't address specific claim details
3. **Claim specificity**: Claims like "founded by **two** men" vs evidence "founded by Arnold Hills and Dave Taylor"

**Improvement Ideas:**
- Stricter evidence matching (implemented in current prompt)
- Two-stage verification (check completeness first)
- Confidence calibration
- See `NEXT_FIXES_FOR_NEI.md` for detailed analysis

## Cost Estimation

Before running evaluation:

```python
# Actual costs (100 samples, gpt-4o, 5 workers)
# Time: ~5-8 minutes
# Cost: ~$15-20

# For gpt-4o-mini (cheaper):
num_samples = 100
cost_per_check = 0.05  
total_cost = num_samples * cost_per_check
# ~$5 for 100 samples
```

## References

- FEVER Dataset: https://fever.ai
- Paper: "FEVER: a large-scale dataset for Fact Extraction and VERification"
- Leaderboard: https://fever.ai/leaderboard.html

