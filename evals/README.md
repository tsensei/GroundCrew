# GroundCrew Evaluations

This directory contains evaluation scripts and results for GroundCrew.

## Files

- **`eval_fever.py`**: FEVER dataset evaluation script with parallel processing
- **`fever_*.json`**: Evaluation results on FEVER dataset

## Latest Results (100 samples, GPT-4o)

| Configuration | Overall | SUPPORTS | REFUTES | NOT ENOUGH INFO |
|---------------|---------|----------|---------|-----------------|
| Web Search    | 71%     | 88%      | 82%     | 42%             |
| Wikipedia-only| 72%     | 91%      | 88%     | 36%             |

## Running Evaluations

```bash
# Standard FEVER evaluation (Wikipedia-only recommended)
poetry run python evals/eval_fever.py -n 100 --wikipedia-only -m gpt-4o

# Quick test
poetry run python evals/eval_fever.py -n 50 --wikipedia-only -m gpt-4o-mini

# Analyze existing results
poetry run python evals/eval_fever.py --analyze -o evals/fever_wiki_only_results.json
```

## Key Findings

### Strengths
- ✅ **Strong SUPPORTS detection**: 88-91% accuracy
- ✅ **Strong REFUTES detection**: 82-88% accuracy
- ✅ **Overall competitive**: 71-72% comparable to specialized systems

### Weaknesses
- ⚠️ **NOT ENOUGH INFO detection**: Only 36-42% accuracy
- **Root cause**: LLM makes confident judgments on partial/related evidence
- **Improvement path**: See `NEXT_FIXES_FOR_NEI.md` in root directory

### Insights
- Wikipedia-only search improves SUPPORTS/REFUTES accuracy
- Web search performs better on NOT ENOUGH INFO (more evidence = more "not enough" triggers)
- System is over-confident (high confidence even on wrong predictions)

## Evaluation Metrics Explained

- **Overall Accuracy**: % of correct predictions across all labels
- **Per-Label Accuracy**: % correct for each specific label
- **Confidence Calibration**: Whether high-confidence predictions are actually more accurate

## Future Evaluations

Potential datasets to add:
- **LIAR**: Political fact-checking (PolitiFact)
- **CLIMATE-FEVER**: Climate science claims
- **MultiFC**: Multi-domain fact-checking
- **Custom**: Domain-specific evaluation sets

## Contributing

To add a new evaluation:
1. Create `eval_<dataset>.py` script
2. Follow similar structure to `eval_fever.py`
3. Save results as `<dataset>_results.json`
4. Update this README with results

