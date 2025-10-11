"""LangGraph workflow for the fact-checking pipeline"""

from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from tavily import TavilyClient

from groundcrew.models import FactCheckState
from groundcrew.agents import (
    ClaimExtractionAgent,
    EvidenceSearchAgent,
    VerificationAgent,
    ReportingAgent
)


# Define the graph state type for LangGraph
class GraphState(TypedDict):
    """State dictionary for LangGraph"""
    state: FactCheckState


def create_fact_check_workflow(
    openai_api_key: str,
    tavily_api_key: str,
    model_name: str = "gpt-4o-mini",
    temperature: float = 0.0
):
    """
    Creates a sequential fact-checking workflow using LangGraph.
    
    Args:
        openai_api_key: OpenAI API key
        tavily_api_key: Tavily API key
        model_name: OpenAI model to use
        temperature: Temperature for LLM responses
        
    Returns:
        Compiled LangGraph workflow
    """
    
    # Initialize LLM and tools
    llm = ChatOpenAI(
        api_key=openai_api_key,
        model=model_name,
        temperature=temperature
    )
    tavily_client = TavilyClient(api_key=tavily_api_key)
    
    # Initialize agents
    claim_agent = ClaimExtractionAgent(llm)
    evidence_agent = EvidenceSearchAgent(llm, tavily_client)
    verification_agent = VerificationAgent(llm)
    reporting_agent = ReportingAgent(llm)
    
    # Define node functions that work with LangGraph state
    def extract_claims_node(state: dict) -> dict:
        """Node for claim extraction"""
        fact_check_state = state["state"]
        updated_state = claim_agent.extract_claims(fact_check_state)
        print(f"✓ Extracted {len(updated_state.claims)} claims")
        return {"state": updated_state}
    
    def search_evidence_node(state: dict) -> dict:
        """Node for evidence retrieval"""
        fact_check_state = state["state"]
        updated_state = evidence_agent.search_evidence(fact_check_state)
        total_evidence = sum(len(ev_list) for ev_list in updated_state.evidence_map.values())
        print(f"✓ Retrieved {total_evidence} pieces of evidence")
        return {"state": updated_state}
    
    def verify_claims_node(state: dict) -> dict:
        """Node for claim verification"""
        fact_check_state = state["state"]
        updated_state = verification_agent.verify_claims(fact_check_state)
        print(f"✓ Verified {len(updated_state.verdicts)} claims")
        return {"state": updated_state}
    
    def generate_report_node(state: dict) -> dict:
        """Node for report generation"""
        fact_check_state = state["state"]
        updated_state = reporting_agent.generate_report(fact_check_state)
        print(f"✓ Generated final report")
        return {"state": updated_state}
    
    # Create the workflow graph
    workflow = StateGraph(dict)
    
    # Add nodes (stages of the pipeline)
    workflow.add_node("extract_claims", extract_claims_node)
    workflow.add_node("search_evidence", search_evidence_node)
    workflow.add_node("verify_claims", verify_claims_node)
    workflow.add_node("generate_report", generate_report_node)
    
    # Define the sequential flow
    workflow.set_entry_point("extract_claims")
    workflow.add_edge("extract_claims", "search_evidence")
    workflow.add_edge("search_evidence", "verify_claims")
    workflow.add_edge("verify_claims", "generate_report")
    workflow.add_edge("generate_report", END)
    
    # Compile the workflow
    app = workflow.compile()
    
    return app


def run_fact_check(
    input_text: str,
    openai_api_key: str,
    tavily_api_key: str,
    model_name: str = "gpt-4o-mini",
    output_file: str = None
) -> FactCheckState:
    """
    Run the complete fact-checking pipeline on input text.
    
    Args:
        input_text: Text to fact-check
        openai_api_key: OpenAI API key
        tavily_api_key: Tavily API key
        model_name: OpenAI model to use
        output_file: Optional path to save report as markdown file
        
    Returns:
        Final FactCheckState with all results
    """
    
    print("\n" + "="*70)
    print("GROUNDCREW - Automated Fact-Checking Workflow")
    print("="*70)
    print(f"\nInput: {input_text[:200]}{'...' if len(input_text) > 200 else ''}\n")
    
    # Create workflow
    workflow = create_fact_check_workflow(
        openai_api_key=openai_api_key,
        tavily_api_key=tavily_api_key,
        model_name=model_name
    )
    
    # Initialize state
    initial_state = FactCheckState(input_text=input_text)
    
    # Run workflow
    print("Pipeline Stages:")
    print("-" * 70)
    
    result = workflow.invoke({"state": initial_state})
    
    print("-" * 70)
    print("\n✅ Fact-checking complete!\n")
    
    final_state = result["state"]
    
    # Save to file if requested
    if output_file:
        _save_report_to_markdown(final_state, output_file)
    
    return final_state


def _save_report_to_markdown(state: FactCheckState, filepath: str) -> None:
    """
    Save fact-check report to a markdown file.
    
    Args:
        state: FactCheckState with results
        filepath: Path to output markdown file
    """
    from datetime import datetime
    
    markdown = f"""# Fact-Check Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Input Text

{state.input_text}

## Summary

- **Claims Found:** {len(state.claims)}
- **Claims Verified:** {len(state.verdicts)}

## Detailed Report

{state.final_report}

## Verdicts

"""
    
    for i, verdict in enumerate(state.verdicts, 1):
        status_emoji = {
            "supported": "✅",
            "refuted": "❌",
            "mixed": "⚠️",
            "not_enough_info": "❓"
        }.get(verdict.status, "•")
        
        markdown += f"""
### {i}. {verdict.claim}

**Status:** {status_emoji} {verdict.status.upper()}  
**Confidence:** {verdict.confidence:.0%}  
**Justification:** {verdict.justification}

"""
        
        if verdict.evidence_used:
            markdown += "**Evidence Sources:**\n\n"
            for j, evidence in enumerate(verdict.evidence_used, 1):
                markdown += f"{j}. [{evidence.source}]({evidence.source})\n"
            markdown += "\n"
    
    # Add error if any
    if state.error:
        markdown += f"\n## Errors\n\n⚠️ {state.error}\n"
    
    markdown += "\n---\n\n*Generated by GroundCrew*\n"
    
    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"📝 Report saved to: {filepath}")

