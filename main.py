"""Main entry point for the GroundCrew fact-checking system"""

import os
import sys
import argparse
from dotenv import load_dotenv

from groundcrew.workflow import run_fact_check


def print_report(state):
    """Pretty print the fact-check report"""
    
    print("\n" + "="*70)
    print("FACT-CHECK REPORT")
    print("="*70)
    print(state.final_report)
    print("\n" + "="*70)
    print("\nDETAILED RESULTS:")
    print("="*70)
    
    for i, verdict in enumerate(state.verdicts, 1):
        print(f"\n[Claim {i}] {verdict.claim}")
        print(f"Status: {verdict.status.upper()} (Confidence: {verdict.confidence:.0%})")
        print(f"Justification: {verdict.justification}")
        
        if verdict.evidence_used:
            print(f"\nEvidence ({len(verdict.evidence_used)} sources):")
            for j, evidence in enumerate(verdict.evidence_used[:3], 1):
                print(f"  {j}. {evidence.source}")
                print(f"     {evidence.snippet[:150]}...")
        print("-" * 70)


def main():
    """Main function"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="GroundCrew - Automated fact-checking system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "The Eiffel Tower is 330 meters tall"
  python main.py "Your claim" --output report.md
  python main.py "Your claim" -o report.md --model gpt-4
        """
    )
    parser.add_argument(
        "text",
        nargs="*",
        help="Text to fact-check (default: example text)"
    )
    parser.add_argument(
        "-o", "--output",
        metavar="FILE",
        help="Save report to markdown file"
    )
    parser.add_argument(
        "-m", "--model",
        default="gpt-4o-mini",
        choices=["gpt-4o-mini", "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
        help="OpenAI model to use (default: gpt-4o-mini)"
    )
    parser.add_argument(
        "--wikipedia-only",
        action="store_true",
        help="Restrict search to Wikipedia only (useful for FEVER-like evaluation)"
    )

    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    
    if not openai_api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please set it in your .env file or export it in your shell")
        sys.exit(1)
    
    if not tavily_api_key:
        print("❌ Error: TAVILY_API_KEY not found in environment variables")
        print("Please set it in your .env file or export it in your shell")
        sys.exit(1)
    
    # Get input text
    if args.text:
        input_text = " ".join(args.text)
    else:
        # Default example text with factual claims
        input_text = """
        The COVID-19 vaccine was developed in record time, with the first vaccines 
        receiving emergency authorization in December 2020. Clinical trials showed 
        that the Pfizer-BioNTech vaccine was 95% effective at preventing COVID-19. 
        According to the CDC, over 600 million doses have been administered in the 
        United States as of 2023. The vaccine uses mRNA technology, which has been 
        in development for over 30 years.
        """
    
    try:
        # Run fact-checking workflow
        search_domain = "wikipedia.org" if args.wikipedia_only else None
        
        result = run_fact_check(
            input_text=input_text.strip(),
            openai_api_key=openai_api_key,
            tavily_api_key=tavily_api_key,
            model_name=args.model,
            output_file=args.output,
            search_domain=search_domain
        )
        
        # Display results
        print_report(result)
        
        # Check for errors
        if result.error:
            print(f"\n⚠️  Warning: {result.error}")
        
    except Exception as e:
        print(f"\n❌ Error during fact-checking: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

