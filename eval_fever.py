"""Evaluate GroundCrew against the FEVER dataset"""

import os
import json
import random
from datetime import datetime
from typing import Dict, List
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from tqdm import tqdm

from groundcrew.workflow import run_fact_check


def map_verdict_to_fever(verdict_status: str) -> str:
    """
    Map GroundCrew verdict status to FEVER labels.
    
    GroundCrew now outputs FEVER-compliant labels directly:
    SUPPORTS, REFUTES, NOT ENOUGH INFO
    
    This function is kept for backwards compatibility but should pass through.
    """
    # GroundCrew now outputs FEVER labels directly
    if verdict_status in ["SUPPORTS", "REFUTES", "NOT ENOUGH INFO"]:
        return verdict_status
    
    # Legacy mapping for old format (backwards compatibility)
    mapping = {
        "supported": "SUPPORTS",
        "refuted": "REFUTES",
        "mixed": "NOT ENOUGH INFO",
        "not_enough_info": "NOT ENOUGH INFO"
    }
    return mapping.get(verdict_status, "NOT ENOUGH INFO")


def create_demo_fever_data(data_dir: str = "data/fever") -> str:
    """
    Create a small demo FEVER dataset for testing.
    
    Args:
        data_dir: Directory to store demo data
        
    Returns:
        Path to the demo.jsonl file
    """
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    demo_file = os.path.join(data_dir, "demo.jsonl")
    
    # Small demo dataset with diverse examples
    demo_data = [
        {"id": 1, "claim": "The Eiffel Tower is located in Paris, France.", "label": "SUPPORTS"},
        {"id": 2, "claim": "The Great Wall of China is visible from space with the naked eye.", "label": "REFUTES"},
        {"id": 3, "claim": "Python was created by Guido van Rossum.", "label": "SUPPORTS"},
        {"id": 4, "claim": "The COVID-19 pandemic began in 2018.", "label": "REFUTES"},
        {"id": 5, "claim": "Mount Everest is the tallest mountain on Earth.", "label": "SUPPORTS"},
        {"id": 6, "claim": "The human brain uses 100% of its capacity at all times.", "label": "REFUTES"},
        {"id": 7, "claim": "Water boils at 100 degrees Celsius at sea level.", "label": "SUPPORTS"},
        {"id": 8, "claim": "Albert Einstein won the Nobel Prize in Chemistry.", "label": "REFUTES"},
        {"id": 9, "claim": "The Amazon River is the longest river in South America.", "label": "SUPPORTS"},
        {"id": 10, "claim": "Sharks are mammals.", "label": "REFUTES"},
        {"id": 11, "claim": "The speed of light is approximately 300,000 kilometers per second.", "label": "SUPPORTS"},
        {"id": 12, "claim": "The Moon is made of cheese.", "label": "REFUTES"},
        {"id": 13, "claim": "DNA stands for deoxyribonucleic acid.", "label": "SUPPORTS"},
        {"id": 14, "claim": "Humans only have four senses.", "label": "REFUTES"},
        {"id": 15, "claim": "The Earth orbits around the Sun.", "label": "SUPPORTS"},
        {"id": 16, "claim": "Napoleon Bonaparte was born in Italy.", "label": "NOT ENOUGH INFO"},
        {"id": 17, "claim": "Coffee is the most consumed beverage in the world.", "label": "NOT ENOUGH INFO"},
        {"id": 18, "claim": "The Pacific Ocean is the largest ocean on Earth.", "label": "SUPPORTS"},
        {"id": 19, "claim": "Goldfish have a three-second memory.", "label": "REFUTES"},
        {"id": 20, "claim": "The human body has 206 bones.", "label": "SUPPORTS"},
    ]
    
    with open(demo_file, 'w', encoding='utf-8') as f:
        for item in demo_data:
            f.write(json.dumps(item) + '\n')
    
    return demo_file


def download_fever_data(data_dir: str = "data/fever") -> str:
    """
    Download FEVER dataset from official source if not already present.
    Falls back to demo data if download fails.
    
    Args:
        data_dir: Directory to store FEVER data
        
    Returns:
        Path to the data file
    """
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    dev_file = os.path.join(data_dir, "shared_task_dev.jsonl")
    
    if os.path.exists(dev_file):
        print(f"✅ Found existing FEVER data at {dev_file}")
        return dev_file
    
    print("📥 Attempting to download FEVER dataset (dev split)...")
    
    # Try multiple download methods
    urls = [
        "https://fever.ai/download/fever/shared_task_dev.jsonl",
        "https://s3-eu-west-1.amazonaws.com/fever.public/shared_task_dev.jsonl",
    ]
    
    for url in urls:
        try:
            import urllib.request
            print(f"Trying: {url}")
            
            # Add headers to mimic browser
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                with open(dev_file, 'wb') as out_file:
                    out_file.write(response.read())
            
            print(f"✅ Downloaded FEVER dataset to {dev_file}")
            return dev_file
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            continue
    
    # If all downloads failed, use demo data
    print("\n⚠️  Could not download full FEVER dataset.")
    print("📝 Creating demo dataset with 20 examples...")
    print("\n💡 To use the full FEVER dataset, manually download:")
    print("   wget -O data/fever/shared_task_dev.jsonl \\")
    print("        https://fever.ai/download/fever/shared_task_dev.jsonl")
    print("   or visit: https://fever.ai/resources.html\n")
    
    return create_demo_fever_data(data_dir)


def load_fever_subset(num_samples: int = 100, data_dir: str = "data/fever") -> List[Dict]:
    """
    Load a subset of the FEVER dataset.
    
    Args:
        num_samples: Number of samples to evaluate
        data_dir: Directory containing FEVER data
        
    Returns:
        List of FEVER examples
    """
    print("Loading FEVER dataset...")
    
    try:
        # Download if needed
        fever_file = download_fever_data(data_dir)
        
        # Load JSONL file
        all_examples = []
        with open(fever_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    all_examples.append(json.loads(line))
        
        print(f"Loaded {len(all_examples)} total examples")
        
        # Sample evenly across labels for balanced evaluation
        by_label = {}
        for ex in all_examples:
            label = ex.get('label', 'NOT ENOUGH INFO')
            if label not in by_label:
                by_label[label] = []
            by_label[label].append(ex)
        
        # Sample proportionally from each label
        subset = []
        samples_per_label = num_samples // len(by_label)
        
        for label, examples in by_label.items():
            random.seed(42)
            sampled = random.sample(examples, min(samples_per_label, len(examples)))
            subset.extend(sampled)
            print(f"  {label}: {len(sampled)} examples")
        
        # If we need more samples, add randomly
        if len(subset) < num_samples:
            remaining = num_samples - len(subset)
            random.seed(42)
            additional = random.sample(all_examples, min(remaining, len(all_examples)))
            subset.extend(additional)
        
        # Shuffle final subset
        random.seed(42)
        random.shuffle(subset)
        subset = subset[:num_samples]
        
        print(f"Selected {len(subset)} examples for evaluation")
        return subset
        
    except Exception as e:
        print(f"Error loading FEVER dataset: {e}")
        print("\nPlease ensure the dataset is downloaded.")
        return []


def process_single_claim(
    item: Dict,
    openai_api_key: str,
    tavily_api_key: str,
    index: int,
    model_name: str = "gpt-4o-mini"
) -> Dict:
    """
    Process a single FEVER claim.
    
    Args:
        item: FEVER dataset item
        openai_api_key: OpenAI API key
        tavily_api_key: Tavily API key
        index: Claim index (for tracking)
        model_name: OpenAI model to use
        
    Returns:
        Result dictionary with prediction and metadata
    """
    try:
        # Extract claim and label
        claim = item.get('claim', '')
        true_label = item.get('label', 'NOT ENOUGH INFO')
        
        # Handle different label formats
        if isinstance(true_label, int):
            label_map = {0: "SUPPORTS", 1: "REFUTES", 2: "NOT ENOUGH INFO"}
            true_label = label_map.get(true_label, "NOT ENOUGH INFO")
        
        # Run GroundCrew fact-check
        result = run_fact_check(
            input_text=claim,
            openai_api_key=openai_api_key,
            tavily_api_key=tavily_api_key,
            model_name=model_name
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
        
        return {
            "index": index,
            "claim": claim,
            "true_label": true_label,
            "predicted_label": predicted_label,
            "correct": is_correct,
            "confidence": confidence,
            "justification": justification[:200],
            "error": result.error if result.error else None
        }
        
    except Exception as e:
        return {
            "index": index,
            "claim": item.get('claim', 'Unknown'),
            "error": str(e),
            "correct": False,
            "true_label": item.get('label', 'NOT ENOUGH INFO'),
            "predicted_label": "NOT ENOUGH INFO",
            "confidence": 0.0,
            "justification": ""
        }


def evaluate_on_fever(
    num_samples: int = 100,
    output_file: str = "fever_evaluation_results.json",
    data_dir: str = "data/fever",
    max_workers: int = 10,
    model_name: str = "gpt-4o-mini"
) -> Dict:
    """
    Evaluate GroundCrew on FEVER dataset with parallel processing.
    
    Args:
        num_samples: Number of samples to evaluate (50-500 recommended)
        output_file: Path to save results
        data_dir: Directory containing FEVER data
        max_workers: Number of parallel workers (default: 10)
        model_name: OpenAI model to use (default: gpt-4o-mini)
        
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
    fever_data = load_fever_subset(num_samples=num_samples, data_dir=data_dir)
    
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
    print(f"Evaluating GroundCrew on FEVER Dataset (Parallel: {max_workers} workers)")
    print(f"{'='*70}\n")
    
    # Process claims in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_item = {
            executor.submit(
                process_single_claim,
                item,
                openai_api_key,
                tavily_api_key,
                i,
                model_name
            ): i for i, item in enumerate(fever_data)
        }
        
        # Process completed tasks with progress bar
        with tqdm(total=len(fever_data), desc="Processing claims") as pbar:
            for future in as_completed(future_to_item):
                try:
                    result_entry = future.result()
                    
                    # Update statistics
                    true_label = result_entry["true_label"]
                    if result_entry["correct"]:
                        correct += 1
                        label_stats[true_label]["correct"] += 1
                    
                    total += 1
                    label_stats[true_label]["total"] += 1
                    
                    results.append(result_entry)
                    
                except Exception as e:
                    print(f"\n⚠️  Error in worker: {e}")
                    total += 1
                
                # Update progress bar
                pbar.update(1)
                
                # Show current accuracy every 10 items
                if total > 0 and total % 10 == 0:
                    current_accuracy = correct / total
                    pbar.set_postfix({"Accuracy": f"{current_accuracy:.2%}"})
    
    # Sort results by original index to maintain order
    results.sort(key=lambda x: x.get("index", 0))
    
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
            "split": "dev",
            "num_samples": len(fever_data),
            "model": model_name,
            "max_workers": max_workers
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
        "--data-dir",
        default="data/fever",
        help="Directory to store/load FEVER data"
    )
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=10,
        help="Number of parallel workers (default: 10)"
    )
    parser.add_argument(
        "-m", "--model",
        default="gpt-4o-mini",
        choices=["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
        help="OpenAI model to use (default: gpt-4o-mini)"
    )
    
    args = parser.parse_args()
    
    if args.analyze:
        analyze_errors(args.output)
    else:
        evaluate_on_fever(
            num_samples=args.num_samples,
            output_file=args.output,
            data_dir=args.data_dir,
            max_workers=args.workers,
            model_name=args.model
        )

