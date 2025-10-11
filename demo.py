"""Comprehensive demo of GroundCrew features"""

import os
import sys
from dotenv import load_dotenv
from groundcrew.workflow import run_fact_check
from groundcrew.models import FactCheckState

# Load environment
load_dotenv()


def check_api_keys():
    """Verify API keys are set"""
    openai_key = os.getenv("OPENAI_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    if not openai_key or not tavily_key:
        print("❌ Error: API keys not found!")
        print("\nPlease set your API keys:")
        print("  1. Copy env.template to .env")
        print("  2. Add your keys:")
        print("     OPENAI_API_KEY=sk-...")
        print("     TAVILY_API_KEY=tvly-...")
        print("\nOr export them:")
        print("  export OPENAI_API_KEY='sk-...'")
        print("  export TAVILY_API_KEY='tvly-...'")
        sys.exit(1)
    
    return openai_key, tavily_key


def demo_simple_claim():
    """Demo 1: Simple factual claim"""
    print("\n" + "="*70)
    print("DEMO 1: Simple Factual Claim")
    print("="*70)
    
    text = "The speed of light in vacuum is approximately 299,792 kilometers per second."
    
    openai_key, tavily_key = check_api_keys()
    
    result = run_fact_check(
        input_text=text,
        openai_api_key=openai_key,
        tavily_api_key=tavily_key,
        model_name="gpt-4o-mini"
    )
    
    print("\n📊 Results:")
    print(result.final_report)
    
    return result


def demo_multiple_claims():
    """Demo 2: Text with multiple claims"""
    print("\n" + "="*70)
    print("DEMO 2: Multiple Claims")
    print("="*70)
    
    text = """
    The Amazon Rainforest produces 20% of the world's oxygen and covers 
    approximately 5.5 million square kilometers. It is home to over 400 
    billion individual trees representing 16,000 species. Deforestation 
    has increased by 50% in the last decade.
    """
    
    openai_key, tavily_key = check_api_keys()
    
    result = run_fact_check(
        input_text=text.strip(),
        openai_api_key=openai_key,
        tavily_api_key=tavily_key,
        model_name="gpt-4o-mini"
    )
    
    print(f"\n📊 Found {len(result.claims)} claims")
    print(f"📊 Generated {len(result.verdicts)} verdicts")
    
    print("\n" + "-"*70)
    for i, verdict in enumerate(result.verdicts, 1):
        status_emoji = {
            "supported": "✅",
            "refuted": "❌",
            "mixed": "⚠️",
            "not_enough_info": "❓"
        }.get(verdict.status, "•")
        
        print(f"\n[{i}] {status_emoji} {verdict.status.upper()}")
        print(f"Claim: {verdict.claim}")
        print(f"Confidence: {verdict.confidence:.0%}")
        print(f"Justification: {verdict.justification[:200]}...")
    
    print("\n" + "-"*70)
    print("\n📄 Full Report:")
    print(result.final_report)
    
    return result


def demo_controversial_claim():
    """Demo 3: Claim that might have mixed evidence"""
    print("\n" + "="*70)
    print("DEMO 3: Controversial/Nuanced Claim")
    print("="*70)
    
    text = """
    Red wine consumption is healthy because it contains resveratrol, 
    which prevents heart disease. Drinking a glass of red wine daily 
    is recommended by most health organizations.
    """
    
    openai_key, tavily_key = check_api_keys()
    
    result = run_fact_check(
        input_text=text.strip(),
        openai_api_key=openai_key,
        tavily_api_key=tavily_key,
        model_name="gpt-4o-mini"
    )
    
    print("\n📊 Results:")
    print(result.final_report)
    
    # Show evidence for each verdict
    print("\n" + "-"*70)
    print("Evidence Sources:")
    print("-"*70)
    
    for i, verdict in enumerate(result.verdicts, 1):
        print(f"\n[Claim {i}] {verdict.claim[:60]}...")
        if verdict.evidence_used:
            for j, evidence in enumerate(verdict.evidence_used[:3], 1):
                print(f"  {j}. {evidence.source}")
        else:
            print("  No evidence found")
    
    return result


def demo_statistics():
    """Demo 4: Statistical claims"""
    print("\n" + "="*70)
    print("DEMO 4: Statistical Claims")
    print("="*70)
    
    text = """
    According to recent studies, 95% of scientists agree on climate change. 
    Global temperatures have risen by 1.5 degrees Celsius since 1850. 
    Sea levels are rising at a rate of 3.3 millimeters per year.
    """
    
    openai_key, tavily_key = check_api_keys()
    
    result = run_fact_check(
        input_text=text.strip(),
        openai_api_key=openai_key,
        tavily_api_key=tavily_key,
        model_name="gpt-4o-mini"
    )
    
    print("\n📊 Results:")
    print(result.final_report)
    
    return result


def interactive_demo():
    """Demo 5: Interactive mode"""
    print("\n" + "="*70)
    print("DEMO 5: Interactive Mode")
    print("="*70)
    print("\nEnter a claim to fact-check (or 'quit' to exit):")
    
    openai_key, tavily_key = check_api_keys()
    
    while True:
        print("\n" + "-"*70)
        text = input("\n🔍 Enter claim: ").strip()
        
        if text.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if not text:
            print("⚠️  Please enter a claim")
            continue
        
        print("\n🔄 Checking...")
        
        try:
            result = run_fact_check(
                input_text=text,
                openai_api_key=openai_key,
                tavily_api_key=tavily_key,
                model_name="gpt-4o-mini"
            )
            
            print("\n📄 Report:")
            print(result.final_report)
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("GroundCrew - Automated Fact-Checking Demo")
    print("="*70)
    
    # Check if API keys are set
    try:
        check_api_keys()
    except SystemExit:
        return
    
    print("\nThis demo will showcase GroundCrew's fact-checking capabilities.")
    print("Each demo may take 30-60 seconds to complete.")
    
    demos = [
        ("Simple Claim", demo_simple_claim),
        ("Multiple Claims", demo_multiple_claims),
        ("Controversial Claim", demo_controversial_claim),
        ("Statistical Claims", demo_statistics),
        ("Interactive Mode", interactive_demo)
    ]
    
    print("\nAvailable demos:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    print("  0. Run all demos")
    
    try:
        choice = input("\nSelect demo (0-5): ").strip()
        
        if choice == "0":
            # Run all demos except interactive
            for name, demo_func in demos[:-1]:
                print(f"\n{'='*70}")
                print(f"Running: {name}")
                print(f"{'='*70}")
                demo_func()
                input("\nPress Enter to continue...")
        elif choice in ["1", "2", "3", "4", "5"]:
            idx = int(choice) - 1
            demos[idx][1]()
        else:
            print("Invalid choice")
            
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

