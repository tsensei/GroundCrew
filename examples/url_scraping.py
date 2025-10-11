"""Example: Fact-check content from a URL using Firecrawl"""

import os
from dotenv import load_dotenv
from firecrawl import Firecrawl

from groundcrew.workflow import run_fact_check

# Load environment variables
load_dotenv()

# API keys
openai_api_key = os.getenv("OPENAI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")
firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")

# URL to fact-check
url = "https://en.wikipedia.org/wiki/Eiffel_Tower"

# Step 1: Scrape content from URL
print(f"🔍 Scraping content from: {url}")
firecrawl = Firecrawl(api_key=firecrawl_api_key)
result = firecrawl.scrape(url, formats=['markdown'])
content = result.markdown
print(f"✓ Scraped {len(content)} characters\n")

# Step 2: Fact-check the content
result = run_fact_check(
    input_text=content,
    openai_api_key=openai_api_key,
    tavily_api_key=tavily_api_key,
    model_name="gpt-4o-mini"
)

# Step 3: Display results
print("\n" + "="*70)
print("FACT-CHECK REPORT")
print("="*70)
print(result.final_report)
print("\n" + "="*70)

# Show verdicts
for i, verdict in enumerate(result.verdicts, 1):
    print(f"\n[Claim {i}] {verdict.claim}")
    print(f"Status: {verdict.status} (Confidence: {verdict.confidence:.0%})")
    print(f"Justification: {verdict.justification}")

