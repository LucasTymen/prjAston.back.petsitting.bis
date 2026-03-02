import pytest
from agents.generator import LmCoordinator, EmailEngine
from core.models import MatchingOutput

@pytest.fixture
def mock_base_json():
    return {
        "meta": {"nom": "Test User"},
        "narratifs_candidature": {"accroche_backend": "Narratif Backend"},
        "experiences": []
    }

def test_lm_coordinator_process(mock_base_json):
    coordinator = LmCoordinator(mock_base_json)
    
    match_data = MatchingOutput(
        persona_selectionne="backend_django",
        secteur_detecte="growth_seo_data_dev",
        exposition_seniorite="Strategique",
        score=90,
        next_action="POSTULER",
        arguments_actives=["Arg1"],
        mots_cles_ats=["Django"]
    )
    
    # Mock LLM chat_completion for LM
    import unittest.mock
    with unittest.mock.patch.object(coordinator.llm, 'chat_completion', return_value={"content": "Monsieur, Madame, Test User est là."}):
        result = coordinator.process(match_data)
        assert isinstance(result, str)
        assert "Test User" in result

def test_email_engine_process(mock_base_json):
    engine = EmailEngine(mock_base_json)
    match_data = MatchingOutput(
        persona_selectionne="backend_django",
        secteur_detecte="growth_seo_data_dev",
        exposition_seniorite="Strategique",
        score=90,
        next_action="POSTULER",
        arguments_actives=["Arg1"],
        mots_cles_ats=["Django"]
    )
    
    import unittest.mock
    with unittest.mock.patch.object(engine.llm, 'chat_completion', return_value={
        "email_j0": "Hello J0",
        "email_j2": "Hello J2",
        "email_j1": "Hello J1",
        "email_j1_bis": "Hello J1 bis",
        "email_j2_bis": "Hello J2 bis",
        "sujet": "Candidature"
    }):
        result = engine.process(match_data)
        assert isinstance(result, dict)
        assert "email_j0" in result
        assert "email_j2" in result
        assert "email_j1" in result
        assert "email_j1_bis" in result
        assert "email_j2_bis" in result
