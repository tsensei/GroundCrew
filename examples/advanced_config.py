"""Advanced example showing configuration options"""

import os
from dotenv import load_dotenv
from groundcrew.workflow import run_fact_check
from groundcrew.config import DEFAULT_CONFIG, HIGH_QUALITY_CONFIG, FAST_CONFIG, GroundCrewConfig

load_dotenv()


def example_default_config():
    """Run with default configuration (balanced)"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Default Configuration")
    print("="*70)
    
    text = "The human brain contains approximately 86 billion neurons."
    
    result = run_fact_check(
        input_text=text,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        tavily_api_key=os.getenv("TAVILY_API_KEY"),
        model_name=DEFAULT_CONFIG.model_name
    )
    
    print(f"\n{result.final_report}\n")


def example_high_quality():
    """Run with high-quality configuration (slower, more thorough)"""
    print("\n" + "="*70)
    print("EXAMPLE 2: High Quality Configuration")
    print("Model: GPT-4, More searches, More evidence")
    print("="*70)
    
    text = """
    Quantum computers use qubits instead of classical bits. A 50-qubit 
    quantum computer can theoretically perform certain calculations faster 
    than any classical supercomputer.
    """
    
    result = run_fact_check(
        input_text=text.strip(),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        tavily_api_key=os.getenv("TAVILY_API_KEY"),
        model_name=HIGH_QUALITY_CONFIG.model_name
    )
    
    print(f"\n{result.final_report}\n")


def example_fast_config():
    """Run with fast configuration (cheaper, quicker)"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Fast Configuration")
    print("Model: GPT-4o-mini, Fewer searches, Basic depth")
    print("="*70)
    
    text = "The Pacific Ocean is the largest ocean on Earth."
    
    result = run_fact_check(
        input_text=text,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        tavily_api_key=os.getenv("TAVILY_API_KEY"),
        model_name=FAST_CONFIG.model_name
    )
    
    print(f"\n{result.final_report}\n")


def example_custom_config():
    """Run with fully custom configuration"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Custom Configuration")
    print("="*70)
    
    # Create custom configuration
    custom_config = GroundCrewConfig(
        model_name="gpt-4o-mini",
        temperature=0.1,  # Slightly more creative
        max_search_results_per_query=4,
        max_queries_per_claim=2,
        search_depth="advanced",
        verbose=True
    )
    
    text = """
    Coffee is one of the most traded commodities in the world. 
    Studies show that moderate coffee consumption may reduce the 
    risk of certain diseases.
    """
    
    result = run_fact_check(
        input_text=text.strip(),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        tavily_api_key=os.getenv("TAVILY_API_KEY"),
        model_name=custom_config.model_name
    )
    
    print(f"\nConfiguration used:")
    print(f"  Model: {custom_config.model_name}")
    print(f"  Temperature: {custom_config.temperature}")
    print(f"  Max queries per claim: {custom_config.max_queries_per_claim}")
    print(f"  Search depth: {custom_config.search_depth}")
    
    print(f"\n{result.final_report}\n")


def compare_models():
    """Compare results between different models"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Model Comparison")
    print("="*70)
    
    text = "Mount Everest is 8,848 meters tall and located in Nepal."
    
    models = ["gpt-4o-mini", "gpt-4"]
    
    for model in models:
        print(f"\n--- Testing with {model} ---")
        
        result = run_fact_check(
            input_text=text,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            tavily_api_key=os.getenv("TAVILY_API_KEY"),
            model_name=model
        )
        
        # Print summary
        print(f"\nClaims found: {len(result.claims)}")
        print(f"Verdicts: {len(result.verdicts)}")
        
        for verdict in result.verdicts:
            print(f"  • {verdict.claim[:50]}...")
            print(f"    Status: {verdict.status} (Confidence: {verdict.confidence:.0%})")


if __name__ == "__main__":
    # Run examples
    # Uncomment the ones you want to try
    
    example_default_config()
    # example_high_quality()  # Requires GPT-4 access, higher cost
    # example_fast_config()
    # example_custom_config()
    # compare_models()  # Requires GPT-4 access

