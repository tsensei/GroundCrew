"""Test NEI improvements on the 33 NOT ENOUGH INFO claims from FEVER"""

import json
import os
from dotenv import load_dotenv
from tqdm import tqdm

from groundcrew.workflow import run_fact_check


def load_nei_claims():
    """Load the 33 NOT ENOUGH INFO claims from previous evaluation"""
    # Load from the Wikipedia-only results (has the most claims)
    with open('evals/fever_wiki_only_results.json', 'r') as f:
        data = json.load(f)
    
    nei_claims = []
    for result in data['individual_results']:
        if result['true_label'] == 'NOT ENOUGH INFO':
            nei_claims.append({
                'claim': result['claim'],
                'true_label': result['true_label'],
                'old_prediction': result.get('predicted_label', 'UNKNOWN'),
                'old_confidence': result.get('confidence', 0.0)
            })
    
    return nei_claims[:33]  # Get first 33


def test_nei_improvements(model_name: str = "gpt-4o"):
    """Test two-stage verification on NEI claims"""
    
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    
    if not openai_api_key or not tavily_api_key:
        raise ValueError("API keys not found")
    
    # Load NEI claims
    nei_claims = load_nei_claims()
    print(f"Testing on {len(nei_claims)} NOT ENOUGH INFO claims\n")
    print("="*70)
    print("TWO-STAGE VERIFICATION TEST")
    print("="*70)
    print("Stage 1: Evidence Completeness Check")
    print("Stage 2: Verdict with Confidence Threshold (0.7)")
    print("="*70 + "\n")
    
    results = []
    correct_before = 0
    correct_after = 0
    
    for i, claim_data in enumerate(tqdm(nei_claims, desc="Testing")):
        try:
            result = run_fact_check(
                input_text=claim_data['claim'],
                openai_api_key=openai_api_key,
                tavily_api_key=tavily_api_key,
                model_name=model_name,
                search_domain="wikipedia.org"  # Use Wikipedia-only for consistency
            )
            
            if result.verdicts:
                new_prediction = result.verdicts[0].status
                new_confidence = result.verdicts[0].confidence
                justification = result.verdicts[0].justification
            else:
                new_prediction = "NOT ENOUGH INFO"
                new_confidence = 0.0
                justification = "No verdict generated"
            
            was_correct_before = (claim_data['old_prediction'] == 'NOT ENOUGH INFO')
            is_correct_now = (new_prediction == 'NOT ENOUGH INFO')
            
            if was_correct_before:
                correct_before += 1
            if is_correct_now:
                correct_after += 1
            
            results.append({
                'claim': claim_data['claim'],
                'true_label': 'NOT ENOUGH INFO',
                'old_prediction': claim_data['old_prediction'],
                'new_prediction': new_prediction,
                'old_confidence': claim_data['old_confidence'],
                'new_confidence': new_confidence,
                'was_correct_before': was_correct_before,
                'is_correct_now': is_correct_now,
                'improved': is_correct_now and not was_correct_before,
                'justification': justification[:150]
            })
            
        except Exception as e:
            print(f"\nError on claim {i}: {e}")
            results.append({
                'claim': claim_data['claim'],
                'error': str(e),
                'is_correct_now': False
            })
    
    # Calculate metrics
    total = len(nei_claims)
    accuracy_before = correct_before / total
    accuracy_after = correct_after / total
    improvement = correct_after - correct_before
    
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"\nTotal NEI claims tested: {total}")
    print(f"\nBefore (baseline):  {correct_before}/{total} correct ({accuracy_before:.1%})")
    print(f"After (two-stage): {correct_after}/{total} correct ({accuracy_after:.1%})")
    print(f"\nImprovement: {'+' if improvement >= 0 else ''}{improvement} claims ({(accuracy_after - accuracy_before):.1%})")
    
    # Show what changed
    newly_correct = [r for r in results if r.get('improved', False)]
    newly_incorrect = [r for r in results if r.get('was_correct_before') and not r.get('is_correct_now')]
    
    print(f"\n✅ Newly correct: {len(newly_correct)}")
    print(f"❌ Newly incorrect: {len(newly_incorrect)}")
    print(f"↔️  No change: {total - len(newly_correct) - len(newly_incorrect)}")
    
    if newly_correct:
        print("\n" + "="*70)
        print("NEWLY CORRECT EXAMPLES")
        print("="*70)
        for i, r in enumerate(newly_correct[:5], 1):
            print(f"\n{i}. {r['claim'][:80]}...")
            print(f"   Before: {r['old_prediction']} → After: {r['new_prediction']} ✅")
            print(f"   Confidence: {r['new_confidence']:.2f}")
            print(f"   Why: {r['justification']}")
    
    if newly_incorrect:
        print("\n" + "="*70)
        print("NEWLY INCORRECT EXAMPLES")
        print("="*70)
        for i, r in enumerate(newly_incorrect[:3], 1):
            print(f"\n{i}. {r['claim'][:80]}...")
            print(f"   Before: {r['old_prediction']} → After: {r['new_prediction']} ❌")
            print(f"   Confidence: {r['new_confidence']:.2f}")
    
    # Prediction distribution
    pred_dist = {}
    for r in results:
        pred = r.get('new_prediction', 'ERROR')
        pred_dist[pred] = pred_dist.get(pred, 0) + 1
    
    print("\n" + "="*70)
    print("NEW PREDICTION DISTRIBUTION")
    print("="*70)
    for pred, count in sorted(pred_dist.items(), key=lambda x: x[1], reverse=True):
        pct = count / total * 100
        print(f"{pred}: {count} ({pct:.1f}%)")
    
    # Save results
    output = {
        'metadata': {
            'total_claims': total,
            'model': model_name,
            'method': 'two-stage-verification-with-confidence-threshold',
            'confidence_threshold': 0.7
        },
        'metrics': {
            'accuracy_before': accuracy_before,
            'accuracy_after': accuracy_after,
            'improvement': improvement,
            'newly_correct': len(newly_correct),
            'newly_incorrect': len(newly_incorrect)
        },
        'prediction_distribution': pred_dist,
        'results': results
    }
    
    output_file = 'evals/nei_improvement_test_results.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n📊 Detailed results saved to: {output_file}")
    print("="*70 + "\n")
    
    return output


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test NEI improvements")
    parser.add_argument(
        "-m", "--model",
        default="gpt-4o",
        choices=["gpt-4o", "gpt-4o-mini", "gpt-4"],
        help="Model to use"
    )
    
    args = parser.parse_args()
    test_nei_improvements(model_name=args.model)

