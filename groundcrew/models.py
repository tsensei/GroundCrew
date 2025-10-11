"""Data models for the fact-checking workflow"""

from typing import List, Literal
from pydantic import BaseModel, Field


class Claim(BaseModel):
    """A single factual claim extracted from text"""
    text: str = Field(description="The claim text")
    priority: int = Field(default=5, description="Priority level (1-10, higher is more important)")


class ClaimsList(BaseModel):
    """List of claims extracted from text"""
    claims: List[Claim] = Field(description="List of factual claims to be verified")


class SearchQueries(BaseModel):
    """Search queries for evidence retrieval"""
    queries: List[str] = Field(description="List of 1-3 search queries to find evidence")


class Evidence(BaseModel):
    """Evidence retrieved for a claim"""
    source: str = Field(description="Source URL or reference")
    snippet: str = Field(description="Relevant text snippet")
    relevance_score: float = Field(default=0.0, description="How relevant this evidence is (0-1)")


class VerdictOutput(BaseModel):
    """Verification verdict output from LLM (without evidence)"""
    status: Literal["SUPPORTS", "REFUTES", "NOT ENOUGH INFO"] = Field(
        description="Truth status of the claim (FEVER-compliant labels)"
    )
    confidence: float = Field(description="Confidence level (0-1)", ge=0.0, le=1.0)
    justification: str = Field(description="Explanation for the verdict")


class Verdict(BaseModel):
    """Verification verdict for a claim"""
    claim: str = Field(description="The original claim")
    status: Literal["SUPPORTS", "REFUTES", "NOT ENOUGH INFO"] = Field(
        description="Truth status of the claim (FEVER-compliant labels)"
    )
    confidence: float = Field(description="Confidence level (0-1)")
    justification: str = Field(description="Explanation for the verdict")
    evidence_used: List[Evidence] = Field(default_factory=list, description="Evidence supporting this verdict")


class FactCheckState(BaseModel):
    """State object that flows through the fact-checking pipeline"""
    # Input
    input_text: str = Field(description="Original text to fact-check")
    
    # Stage 1: Claim Detection
    claims: List[Claim] = Field(default_factory=list, description="Extracted claims")
    
    # Stage 2: Evidence Retrieval
    evidence_map: dict[str, List[Evidence]] = Field(
        default_factory=dict, 
        description="Map of claim text to evidence list"
    )
    
    # Stage 3: Verification
    verdicts: List[Verdict] = Field(default_factory=list, description="Verification results")
    
    # Stage 4: Communication
    final_report: str = Field(default="", description="Human-readable report")
    
    # Metadata
    error: str = Field(default="", description="Error message if any")


class FactCheckReport(BaseModel):
    """Final fact-check report"""
    input_text: str
    claims_found: int
    verdicts: List[Verdict]
    summary: str
    timestamp: str

