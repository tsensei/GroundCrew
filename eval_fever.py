"""Evaluate GroundCrew against the FEVER dataset"""

import os
import json
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv
from datasets import load_dataset
from tqdm import tqdm

from groundcrew.workflow import run_fact_check


def map_verdict_to_fever(verdict_status: str) -> str:
    """
    Map GroundCrew verdict status to FEVER labels.
    
    GroundCrew: supported, refuted, mixed, not_enough_info
    FEVER: SUPPORTS, REFUTES, NOT ENOUGH INFO
    """
    mapping = {
        "supported": "SUPPORTS",
        "refuted": "REFUTES",
        "mixed": "NOT ENOUGH INFO",  # Conservative: treat mixed as NEI
        "not_enough_info": "NOT ENOUGH INFO"
    }
    return mapping.get(verdict_status, "NOT ENOUGH INFO")


def load_fever_subset(split: str = "validation", num_samples: int = 100) -> List[Dict]:
    """
    Load a subset of the FEVER dataset.
    
    Args:
        split: Dataset split to use (train, validation, test)
        num_samples: Number of samples to evaluate
        
    Returns:
        List of FEVER examples
    """
    print(f"Loading FEVER dataset ({split} split)...")
    
    try:
        # Load FEVER dataset from Hugging Face
        dataset = load_dataset("fever", "v1.0", split=split)
        
        # Get a subset
        if num_samples < len(dataset):
            # Sample evenly across labels for balanced evaluation
            subset = dataset.shuffle(seed=42).select(range(num_samples))
        else:
            subset = dataset
        
        print(f"Loaded {len(subset)} examples")
        return subset
        
    except Exception as e:
        print(f"Error loading FEVER dataset: {e}")
        print("Trying alternative dataset name...")
        
        # Fallback: try different dataset name
        try:
            dataset = load_dataset("pietrolesci/fever-nli", split="train")
            subset = dataset.shuffle(seed=42).select(range(min(num_samples, len(dataset))))
            print(f"Loaded {len(subset)} examples from alternative source")
            return subset
        except Exception as e2:
            print(f"Failed to load dataset: {e2}")
            print("\nPlease manually download FEVER dataset or use demo mode.")
            return []


def evaluate_on_fever(
    num_samples: int = 100,
    output_file: str = "fever_evaluation_results.json",
    split: str = "validation"
) -> Dict:
    """
    Evaluate GroundCrew on FEVER dataset.
    
    Args:
        num_samples: Number of samples to evaluate (50-500 recommended)
        output_file: Path to save results
        split: Dataset split to use
        
    Returns:
        Dictionary with evaluation metrics and results
    """
    
    # Load environment variables
    load_dotenv()
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    
    if not openai_api_key or not tavily_api_key:
        raise ValueError("API keys not found. Please set OPENAI_API_KEY and TAVILY_API_KEY")
    
    # Load FEVER data
    fever_data = load_fever_subset(split=split, num_samples=num_samples)
    
    if not fever_data:
        print("No data loaded. Exiting.")
        return {}
    
    # Evaluation results
    results = []
    correct = 0
    total = 0
    
    # Label counts
    label_stats = {
        "SUPPORTS": {"correct": 0, "total": 0},
        "REFUTES": {"correct": 0, "total": 0},
        "NOT ENOUGH INFO": {"correct": 0, "total": 0}
    }
    
    print(f"\n{'='*70}")
    print("Evaluating GroundCrew on FEVER Dataset")
    print(f"{'='*70}\n")
    
    # Process each claim
    for i, item in enumerate(tqdm(fever_data, desc="Processing claims")):
        try:
            # Extract claim and label
            claim = item.get('claim', '')
            true_label = item.get('label', 'NOT ENOUGH INFO')
            
            # Handle different label formats
            if isinstance(true_label, int):
                # Some versions use integer labels
                label_map = {0: "SUPPORTS", 1: "REFUTES", 2: "NOT ENOUGH INFO"}
                true_label = label_map.get(true_label, "NOT ENOUGH INFO")
            
            # Run GroundCrew fact-check
            result = run_fact_check(
                input_text=claim,
                openai_api_key=openai_api_key,
                tavily_api_key=tavily_api_key,
                model_name="gpt-4o-mini"
            )
            
            # Get prediction
            if result.verdicts:
                predicted_status = result.verdicts[0].status
                predicted_label = map_verdict_to_fever(predicted_status)
                confidence = result.verdicts[0].confidence
                justification = result.verdicts[0].justification
            else:
                predicted_label = "NOT ENOUGH INFO"
                confidence = 0.0
                justification = "No verdict generated"
            
            # Check correctness
            is_correct = (predicted_label == true_label)
            
            if is_correct:
                correct += 1
                label_stats[true_label]["correct"] += 1
            
            total += 1
            label_stats[true_label]["total"] += 1
            
            # Store result
            result_entry = {
                "claim": claim,
                "true_label": true_label,
                "predicted_label": predicted_label,
                "correct": is_correct,
                "confidence": confidence,
                "justification": justification[:200],  # Truncate for readability
                "error": result.error if result.error else None
            }
            results.append(result_entry)
            
            # Print progress every 10 items
            if (i + 1) % 10 == 0:
                current_accuracy = correct / total
                print(f"\nProgress: {i+1}/{len(fever_data)} | Accuracy: {current_accuracy:.2%}")
        
        except Exception as e:
            print(f"\nError processing claim {i+1}: {e}")
            results.append({
                "claim": claim if 'claim' in locals() else "Unknown",
                "error": str(e),
                "correct": False
            })
            total += 1
    
    # Calculate final metrics
    accuracy = correct / total if total > 0 else 0
    
    # Calculate per-label metrics
    per_label_metrics = {}
    for label, stats in label_stats.items():
        if stats["total"] > 0:
            label_accuracy = stats["correct"] / stats["total"]
            per_label_metrics[label] = {
                "accuracy": label_accuracy,
                "correct": stats["correct"],
                "total": stats["total"]
            }
    
    # Calculate confidence calibration
    confidence_bins = {
        "high (>0.8)": {"correct": 0, "total": 0},
        "medium (0.5-0.8)": {"correct": 0, "total": 0},
        "low (<0.5)": {"correct": 0, "total": 0}
    }
    
    for r in results:
        if "confidence" in r:
            conf = r["confidence"]
            if conf > 0.8:
                bin_name = "high (>0.8)"
            elif conf >= 0.5:
                bin_name = "medium (0.5-0.8)"
            else:
                bin_name = "low (<0.5)"
            
            confidence_bins[bin_name]["total"] += 1
            if r["correct"]:
                confidence_bins[bin_name]["correct"] += 1
    
    # Prepare evaluation summary
    evaluation_summary = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "dataset": "FEVER",
            "split": split,
            "num_samples": len(fever_data),
            "model": "gpt-4o-mini"
        },
        "overall_metrics": {
            "accuracy": accuracy,
            "correct": correct,
            "total": total
        },
        "per_label_metrics": per_label_metrics,
        "confidence_calibration": {
            bin_name: {
                "accuracy": stats["correct"] / stats["total"] if stats["total"] > 0 else 0,
                "count": stats["total"]
            }
            for bin_name, stats in confidence_bins.items()
        },
        "individual_results": results
    }
    
    # Save results to file
    with open(output_file, 'w') as f:
        json.dump(evaluation_summary, f, indent=2)
    
    # Print summary
    print(f"\n{'='*70}")
    print("EVALUATION SUMMARY")
    print(f"{'='*70}")
    print(f"\nOverall Accuracy: {accuracy:.2%} ({correct}/{total})")
    print("\nPer-Label Performance:")
    for label, metrics in per_label_metrics.items():
        print(f"  {label}: {metrics['accuracy']:.2%} ({metrics['correct']}/{metrics['total']})")
    
    print("\nConfidence Calibration:")
    for bin_name, metrics in evaluation_summary["confidence_calibration"].items():
        if metrics["count"] > 0:
            print(f"  {bin_name}: {metrics['accuracy']:.2%} ({metrics['count']} predictions)")
    
    print(f"\n📊 Detailed results saved to: {output_file}")
    print(f"{'='*70}\n")
    
    return evaluation_summary


def analyze_errors(results_file: str = "fever_evaluation_results.json"):
    """
    Analyze errors from FEVER evaluation results.
    
    Args:
        results_file: Path to evaluation results JSON
    """
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    results = data.get("individual_results", [])
    errors = [r for r in results if not r.get("correct", False)]
    
    print(f"\n{'='*70}")
    print(f"ERROR ANALYSIS ({len(errors)} errors)")
    print("="*70 + "\n")
    
    # Group errors by prediction type
    error_types = {}
    for error in errors:
        key = f"{error.get('true_label', 'Unknown')} → {error.get('predicted_label', 'Unknown')}"
        if key not in error_types:
            error_types[key] = []
        error_types[key].append(error)
    
    # Print error patterns
    print("Error Patterns:")
    for error_type, examples in sorted(error_types.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n{error_type}: {len(examples)} cases")
        # Show first example
        if examples:
            ex = examples[0]
            print(f"  Example: {ex['claim'][:100]}...")
            print(f"  Confidence: {ex.get('confidence', 0):.2f}")
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Evaluate GroundCrew against FEVER dataset"
    )
    parser.add_argument(
        "-n", "--num-samples",
        type=int,
        default=100,
        help="Number of samples to evaluate (50-500 recommended)"
    )
    parser.add_argument(
        "-o", "--output",
        default="fever_evaluation_results.json",
        help="Output file for results"
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze existing results file"
    )
    parser.add_argument(
        "--split",
        default="validation",
        choices=["train", "validation", "test"],
        help="Dataset split to use"
    )
    
    args = parser.parse_args()
    
    if args.analyze:
        analyze_errors(args.output)
    else:
        evaluate_on_fever(
            num_samples=args.num_samples,
            output_file=args.output,
            split=args.split
        )

