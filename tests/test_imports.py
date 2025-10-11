"""Test that all modules can be imported successfully"""

def test_import_models():
    """Test importing models module"""
    from groundcrew import models
    assert hasattr(models, 'Claim')
    assert hasattr(models, 'Evidence')
    assert hasattr(models, 'Verdict')
    assert hasattr(models, 'FactCheckState')


def test_import_agents():
    """Test importing agents module"""
    from groundcrew import agents
    assert hasattr(agents, 'ClaimExtractionAgent')
    assert hasattr(agents, 'EvidenceSearchAgent')
    assert hasattr(agents, 'VerificationAgent')
    assert hasattr(agents, 'ReportingAgent')


def test_import_workflow():
    """Test importing workflow module"""
    from groundcrew import workflow
    assert hasattr(workflow, 'create_fact_check_workflow')
    assert hasattr(workflow, 'run_fact_check')


def test_version():
    """Test package version"""
    import groundcrew
    assert hasattr(groundcrew, '__version__')
    assert groundcrew.__version__ == "0.1.0"

