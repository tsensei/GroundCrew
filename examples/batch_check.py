"""Example of batch fact-checking multiple texts"""

import os
from dotenv import load_dotenv
from groundcrew.workflow import run_fact_check

load_dotenv()


def batch_fact_check(texts: list[str]):
    """Run fact-checking on multiple texts"""
    
    results = []
    
    for i, text in enumerate(texts, 1):
        print(f"\n{'='*70}")
        print(f"CHECKING TEXT {i}/{len(texts)}")
        print(f"{'='*70}")
        print(f"Text: {text[:100]}...")
        
        result = run_fact_check(
            input_text=text,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            tavily_api_key=os.getenv("TAVILY_API_KEY"),
            model_name="gpt-4o-mini"
        )
        
        results.append({
            "text": text,
            "claims_found": len(result.claims),
            "verdicts": result.verdicts,
            "report": result.final_report
        })
    
    return results


if __name__ == "__main__":
    # Example: Fact-check multiple news snippets
    texts_to_check = [
        """
        The James Webb Space Telescope, launched in 2021, is the most 
        powerful space telescope ever built. It can see further into the 
        universe than any previous telescope.
        """,
        
        """
        Electric vehicles produce zero emissions. Studies show that EVs 
        are always better for the environment than gasoline cars.
        """,
        
        """
        Antarctica is the driest continent on Earth. Some parts of Antarctica 
        haven't seen rain for nearly 2 million years.
        """,
        
        """
        The Great Barrier Reef is the largest living structure on Earth, 
        visible from space. It spans over 2,300 kilometers off the coast 
        of Australia.
        """
    ]
    
    # Run batch check
    print("\n🚀 Starting batch fact-check...")
    print(f"Processing {len(texts_to_check)} texts\n")
    
    results = batch_fact_check(texts_to_check)
    
    # Summary
    print("\n" + "="*70)
    print("BATCH SUMMARY")
    print("="*70)
    
    for i, result in enumerate(results, 1):
        print(f"\nText {i}:")
        print(f"  Claims: {result['claims_found']}")
        print(f"  Verdicts:")
        
        for verdict in result['verdicts']:
            status_emoji = {
                "SUPPORTS": "✅",
                "REFUTES": "❌",
                "NOT ENOUGH INFO": "❓"
            }.get(verdict.status, "•")
            
            print(f"    {status_emoji} {verdict.status.upper()} - {verdict.claim[:60]}...")
    
    print("\n✅ Batch processing complete!")

