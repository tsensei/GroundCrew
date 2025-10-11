"""Configuration settings for GroundCrew"""

from typing import Literal
from pydantic import BaseModel, Field


class GroundCrewConfig(BaseModel):
    """Configuration for the fact-checking workflow"""
    
    # Model settings
    model_name: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model to use (gpt-4o-mini, gpt-4, gpt-4-turbo, etc.)"
    )
    temperature: float = Field(
        default=0.0,
        description="Temperature for LLM responses (0.0 = deterministic, 1.0 = creative)",
        ge=0.0,
        le=2.0
    )
    
    # Search settings
    max_search_results_per_query: int = Field(
        default=3,
        description="Maximum number of search results to retrieve per query",
        ge=1,
        le=10
    )
    max_queries_per_claim: int = Field(
        default=2,
        description="Maximum number of search queries to generate per claim",
        ge=1,
        le=5
    )
    search_depth: Literal["basic", "advanced"] = Field(
        default="advanced",
        description="Tavily search depth (basic or advanced)"
    )
    
    # Evidence settings
    max_evidence_per_claim: int = Field(
        default=5,
        description="Maximum pieces of evidence to collect per claim",
        ge=1,
        le=20
    )
    snippet_max_length: int = Field(
        default=500,
        description="Maximum length of evidence snippets (characters)",
        ge=100,
        le=2000
    )
    
    # Verification settings
    evidence_for_verdict: int = Field(
        default=3,
        description="Number of top evidence pieces to include in verdicts",
        ge=1,
        le=10
    )
    
    # Output settings
    verbose: bool = Field(
        default=True,
        description="Print progress messages during execution"
    )
    
    class Config:
        """Pydantic config"""
        validate_assignment = True


# Default configuration
DEFAULT_CONFIG = GroundCrewConfig()

# High-quality configuration (slower, more accurate)
HIGH_QUALITY_CONFIG = GroundCrewConfig(
    model_name="gpt-4",
    max_search_results_per_query=5,
    max_queries_per_claim=3,
    max_evidence_per_claim=10
)

# Fast configuration (faster, lower cost)
FAST_CONFIG = GroundCrewConfig(
    model_name="gpt-4o-mini",
    max_search_results_per_query=2,
    max_queries_per_claim=1,
    max_evidence_per_claim=3,
    search_depth="basic"
)

