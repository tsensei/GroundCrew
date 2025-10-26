"""Example: Using TCC custom metadata for observability"""

import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Import and initialize TCC instrumentation BEFORE importing LangGraph/LangChain
from tcc_otel import instrument_langchain

instrument_langchain(
    api_key=os.getenv("TCC_API_KEY"),
)

# Now import the rest of the dependencies
from groundcrew.workflow import run_fact_check


def example_with_user_metadata():
    """Example: Tag agent runs with user ID for filtering"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Tagging with User ID")
    print("="*70)

    text = "The Eiffel Tower is 330 meters tall and was completed in 1889."

    result = run_fact_check(
        input_text=text,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        tavily_api_key=os.getenv("TAVILY_API_KEY"),
        model_name="gpt-4o-mini",
        # Add custom metadata to track this agent run
        metadata={
            "userId": "4a6b111c-b53a-4d00-a877-67185022ab9e",
            "feature": "fact-check",
        }
    )

    print(f"\n✓ Agent run tagged with userId: 4a6b111c-b53a-4d00-a877-67185022ab9e")
    print(f"✓ Found {len(result.verdicts)} verdicts")


def example_with_organization_metadata():
    """Example: Tag agent runs with organization for multi-tenant apps"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Tagging with Organization")
    print("="*70)

    text = "Python was created by Guido van Rossum and first released in 1991."

    result = run_fact_check(
        input_text=text,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        tavily_api_key=os.getenv("TAVILY_API_KEY"),
        model_name="gpt-4o-mini",
        # Add organization metadata
        metadata={
            "organizationId": "acme-corp",
            "department": "research",
            "project": "fact-verification",
        }
    )

    print(f"\n✓ Agent run tagged with organizationId: acme-corp")
    print(f"✓ Department: research, Project: fact-verification")


def example_with_request_context():
    """Example: Tag agent runs with request context"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Tagging with Request Context")
    print("="*70)

    text = "The speed of light is approximately 299,792 km/s."

    result = run_fact_check(
        input_text=text,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        tavily_api_key=os.getenv("TAVILY_API_KEY"),
        model_name="gpt-4o-mini",
        # Add request context metadata
        metadata={
            "requestId": "req_abc123",
            "sessionId": "sess_xyz789",
            "source": "api",
            "environment": "production",
        }
    )

    print(f"\n✓ Agent run tagged with requestId: req_abc123")
    print(f"✓ Environment: production")


def example_batch_with_metadata():
    """Example: Batch processing with different metadata per request"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Batch Processing with Metadata")
    print("="*70)

    claims = [
        ("The Pacific Ocean is the largest ocean.", "user-123"),
        ("Mount Everest is the tallest mountain on Earth.", "user-456"),
        ("The Amazon River is the longest river.", "user-789"),
    ]

    for text, user_id in claims:
        print(f"\n📝 Processing claim for {user_id}...")

        result = run_fact_check(
            input_text=text,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            tavily_api_key=os.getenv("TAVILY_API_KEY"),
            model_name="gpt-4o-mini",
            # Each request gets its own metadata
            metadata={
                "userId": user_id,
                "claimType": "geography",
                "batch": "batch-001",
            }
        )

        print(f"✓ Completed for {user_id}: {result.verdicts[0].status if result.verdicts else 'N/A'}")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("TCC Custom Metadata Examples")
    print("="*70)
    print("\nThese examples show how to tag agent runs with custom metadata")
    print("for filtering and analysis in the TCC dashboard.\n")

    # Check if TCC_API_KEY is set
    if not os.getenv("TCC_API_KEY"):
        print("⚠️  Warning: TCC_API_KEY not found in environment variables")
        print("   Agent runs will still work but won't be tracked in TCC dashboard.")
        print("   Add TCC_API_KEY to your .env file to enable observability.\n")

    # Run examples
    example_with_user_metadata()
    example_with_organization_metadata()
    example_with_request_context()
    # example_batch_with_metadata()  # Uncomment to run batch example

    print("\n" + "="*70)
    print("✅ All examples completed!")
    print("="*70)
    print("\nNext steps:")
    print("  1. View your agent runs in the TCC dashboard")
    print("  2. Filter by custom metadata fields (userId, organizationId, etc.)")
    print("  3. Analyze performance across different user segments")


if __name__ == "__main__":
    main()
