"""Agent implementations for each stage of the fact-checking pipeline"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from tavily import TavilyClient

from groundcrew.models import (
    Claim, 
    ClaimsList, 
    Evidence, 
    SearchQueries,
    Verdict, 
    VerdictOutput,
    FactCheckState
)


class ClaimExtractionAgent:
    """Agent responsible for detecting and extracting check-worthy claims"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        # Create structured output LLM
        self.structured_llm = llm.with_structured_output(ClaimsList)
    
    def extract_claims(self, state: FactCheckState) -> FactCheckState:
        """Extract claims from input text"""
        prompt = f"""You are an expert claim extraction agent for fact-checking.
Your task is to identify specific factual claims that can be verified from the given text.

Focus on:
- Factual statements that can be true or false
- Statistical claims, dates, numbers
- Claims about events, people, or entities
- Statements that require evidence to verify

Avoid:
- Opinions or subjective statements
- Questions
- General statements without specific facts

Extract factual claims from this text and assign each a priority (1-10, higher is more important):

{state.input_text}"""
        
        try:
            result: ClaimsList = self.structured_llm.invoke(prompt)
            state.claims = sorted(result.claims, key=lambda x: x.priority, reverse=True)
        except Exception as e:
            state.error = f"Claim extraction error: {str(e)}"
            # Fallback: treat entire input as single claim
            state.claims = [Claim(text=state.input_text, priority=5)]
        
        return state


class EvidenceSearchAgent:
    """Agent responsible for retrieving evidence for claims"""
    
    def __init__(self, llm: ChatOpenAI, tavily_client: TavilyClient):
        self.llm = llm
        self.tavily = tavily_client
        # Create structured output LLM
        self.structured_llm = llm.with_structured_output(SearchQueries)
    
    def search_evidence(self, state: FactCheckState) -> FactCheckState:
        """Search for evidence for each claim"""
        evidence_map = {}
        
        for claim in state.claims:
            # Generate search queries using structured output
            prompt = f"""You are an expert at formulating search queries for fact-checking.
Given a claim, create 1-3 effective search queries that would help verify or refute the claim.

Claim: {claim.text}

Generate search queries that will find relevant evidence."""
            
            try:
                result: SearchQueries = self.structured_llm.invoke(prompt)
                queries = result.queries
            except Exception as e:
                print(f"Query generation error: {str(e)}")
                # Fallback: use claim text as query
                queries = [claim.text]
            
            # Search with Tavily
            evidence_list = []
            for query in queries[:2]:  # Limit to 2 queries per claim
                try:
                    search_results = self.tavily.search(
                        query=query,
                        max_results=3,
                        search_depth="advanced"
                    )
                    
                    for result in search_results.get('results', []):
                        evidence = Evidence(
                            source=result.get('url', ''),
                            snippet=result.get('content', '')[:500],  # Limit snippet length
                            relevance_score=result.get('score', 0.5)
                        )
                        evidence_list.append(evidence)
                except Exception as e:
                    print(f"Search error for query '{query}': {str(e)}")
                    continue
            
            evidence_map[claim.text] = evidence_list
        
        state.evidence_map = evidence_map
        return state


class VerificationAgent:
    """Agent responsible for verifying claims against evidence"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        # Create structured output LLM
        self.structured_llm = llm.with_structured_output(VerdictOutput)
    
    def verify_claims(self, state: FactCheckState) -> FactCheckState:
        """Verify each claim against its evidence"""
        verdicts = []
        
        for claim in state.claims:
            evidence_list = state.evidence_map.get(claim.text, [])
            
            # Format evidence for the LLM
            evidence_text = "\n\n".join([
                f"Source: {ev.source}\nSnippet: {ev.snippet}"
                for ev in evidence_list[:5]  # Limit to top 5 evidence pieces
            ])
            
            if not evidence_text:
                evidence_text = "No evidence found."
            
            prompt = f"""You are an expert fact-checker responsible for verifying claims.
Analyze the claim and the evidence provided, then determine:
1. Status: "supported", "refuted", "mixed", or "not_enough_info"
2. Confidence: a score from 0 to 1
3. Justification: a clear explanation of your reasoning

Be objective and base your verdict strictly on the evidence provided.

Claim: {claim.text}

Evidence:
{evidence_text}

Provide your verdict:"""
            
            try:
                verdict_output: VerdictOutput = self.structured_llm.invoke(prompt)
                verdict = Verdict(
                    claim=claim.text,
                    status=verdict_output.status,
                    confidence=verdict_output.confidence,
                    justification=verdict_output.justification,
                    evidence_used=evidence_list[:3]  # Include top 3 evidence pieces
                )
                verdicts.append(verdict)
            except Exception as e:
                # Fallback verdict
                verdicts.append(Verdict(
                    claim=claim.text,
                    status="not_enough_info",
                    confidence=0.0,
                    justification=f"Error processing verdict: {str(e)}",
                    evidence_used=evidence_list[:3]
                ))
        
        state.verdicts = verdicts
        return state


class ReportingAgent:
    """Agent responsible for generating the final fact-check report"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.system_prompt = """You are an expert at communicating fact-check results clearly.
Create a comprehensive, well-structured report that presents the fact-check findings.

The report should:
- Be clear and accessible to general readers
- Present each claim with its verdict and evidence
- Explain the reasoning behind each verdict
- Provide an overall summary

Use clear formatting with sections and bullet points where appropriate."""
    
    def generate_report(self, state: FactCheckState) -> FactCheckState:
        """Generate final human-readable report"""
        
        # Format verdicts for the LLM
        verdicts_text = ""
        for i, verdict in enumerate(state.verdicts, 1):
            verdicts_text += f"\n\nClaim {i}: {verdict.claim}\n"
            verdicts_text += f"Status: {verdict.status.upper()}\n"
            verdicts_text += f"Confidence: {verdict.confidence:.0%}\n"
            verdicts_text += f"Justification: {verdict.justification}\n"
            if verdict.evidence_used:
                verdicts_text += "Key Evidence:\n"
                for ev in verdict.evidence_used[:2]:
                    verdicts_text += f"  - {ev.source}\n"
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Original Text: {state.input_text}

Fact-Check Results:{verdicts_text}

Generate a comprehensive fact-check report:""")
        ]
        
        response = self.llm.invoke(messages)
        state.final_report = response.content
        
        return state

