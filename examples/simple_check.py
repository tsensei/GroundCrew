"""Simple example of using GroundCrew for fact-checking"""

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

# Example 1: Simple factual claim
text1 = "The Earth orbits around the Sun, completing one orbit every 365.25 days."

# Example 2: Multiple claims with statistics
text2 = """
The global temperature has increased by 1.1°C since pre-industrial times.
Scientists estimate that if current trends continue, we could see a 3°C 
increase by 2100. Over 97% of climate scientists agree that climate change 
is caused by human activities.
"""

# Example 3: Questionable claim
text3 = "Drinking 8 glasses of water per day is scientifically proven to be necessary for optimal health."

# Choose which example to run
example_text = text2

print("Running fact-check on example text...")
print(f"Text: {example_text.strip()}\n")

result = run_fact_check(
    input_text=example_text.strip(),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    tavily_api_key=os.getenv("TAVILY_API_KEY"),
    model_name="gpt-4o-mini"
)

print("\n" + "="*70)
print("FINAL REPORT")
print("="*70)
print(result.final_report)

