"""Tests for data models"""

import pytest
from groundcrew.models import (
    Claim, 
    ClaimsList,
    Evidence, 
    SearchQueries,
    Verdict,
    VerdictOutput,
    FactCheckState
)


def test_claim_creation():
    """Test Claim model"""
    claim = Claim(text="Python was created in 1991", priority=8)
    assert claim.text == "Python was created in 1991"
    assert claim.priority == 8


def test_claim_default_priority():
    """Test Claim default priority"""
    claim = Claim(text="Test claim")
    assert claim.priority == 5


def test_evidence_creation():
    """Test Evidence model"""
    evidence = Evidence(
        source="https://example.com",
        snippet="Some evidence text",
        relevance_score=0.9
    )
    assert evidence.source == "https://example.com"
    assert evidence.snippet == "Some evidence text"
    assert evidence.relevance_score == 0.9


def test_verdict_creation():
    """Test Verdict model"""
    verdict = Verdict(
        claim="Test claim",
        status="SUPPORTS",
        confidence=0.95,
        justification="Evidence supports the claim"
    )
    assert verdict.claim == "Test claim"
    assert verdict.status == "SUPPORTS"
    assert verdict.confidence == 0.95


def test_fact_check_state_creation():
    """Test FactCheckState model"""
    state = FactCheckState(input_text="Test input")
    assert state.input_text == "Test input"
    assert state.claims == []
    assert state.evidence_map == {}
    assert state.verdicts == []
    assert state.final_report == ""
    assert state.error == ""


def test_fact_check_state_with_claims():
    """Test FactCheckState with claims"""
    claim1 = Claim(text="Claim 1", priority=7)
    claim2 = Claim(text="Claim 2", priority=5)
    
    state = FactCheckState(
        input_text="Test",
        claims=[claim1, claim2]
    )
    
    assert len(state.claims) == 2
    assert state.claims[0].text == "Claim 1"


def test_verdict_status_validation():
    """Test Verdict status validation"""
    # Valid statuses (FEVER-compliant labels)
    for status in ["SUPPORTS", "REFUTES", "NOT ENOUGH INFO"]:
        verdict = Verdict(
            claim="Test",
            status=status,
            confidence=0.8,
            justification="Test"
        )
        assert verdict.status == status


def test_claims_list_creation():
    """Test ClaimsList model for structured output"""
    claims = [
        Claim(text="Claim 1", priority=8),
        Claim(text="Claim 2", priority=5)
    ]
    claims_list = ClaimsList(claims=claims)
    
    assert len(claims_list.claims) == 2
    assert claims_list.claims[0].text == "Claim 1"
    assert claims_list.claims[1].priority == 5


def test_search_queries_creation():
    """Test SearchQueries model for structured output"""
    queries = SearchQueries(queries=["query 1", "query 2", "query 3"])
    
    assert len(queries.queries) == 3
    assert queries.queries[0] == "query 1"


def test_verdict_output_creation():
    """Test VerdictOutput model for structured output"""
    verdict_output = VerdictOutput(
        status="SUPPORTS",
        confidence=0.95,
        justification="Evidence clearly supports the claim"
    )
    
    assert verdict_output.status == "SUPPORTS"
    assert verdict_output.confidence == 0.95
    assert verdict_output.justification == "Evidence clearly supports the claim"


def test_verdict_output_confidence_bounds():
    """Test VerdictOutput confidence is bounded between 0 and 1"""
    # Valid confidence
    verdict = VerdictOutput(
        status="SUPPORTS",
        confidence=0.5,
        justification="Test"
    )
    assert 0.0 <= verdict.confidence <= 1.0
    
    # Test edge cases
    verdict_min = VerdictOutput(
        status="NOT ENOUGH INFO",
        confidence=0.0,
        justification="No evidence"
    )
    assert verdict_min.confidence == 0.0
    
    verdict_max = VerdictOutput(
        status="SUPPORTS",
        confidence=1.0,
        justification="Conclusive evidence"
    )
    assert verdict_max.confidence == 1.0

