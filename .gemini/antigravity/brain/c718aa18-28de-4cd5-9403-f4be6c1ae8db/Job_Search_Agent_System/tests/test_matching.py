import pytest
from agents.matching import MatchingEngine
from core.models import ScraperOutput

@pytest.fixture
def mock_base_json():
    """base_json avec personas pour MatchingEngine déterministe."""
    return {
        "meta": {"nom": "Test"},
        "experiences": [],
        "personas_specialises": {
            "expert_python": {
                "mots_cles_detection": ["Python", "backend", "API"],
                "arguments_prioritaires": ["Usage intensif de Python"],
            },
        },
        "persona_engine": {"poids_par_type": {"competence_technique": 3}},
    }

def test_matching_engine_process(mock_base_json):
    """MatchingEngine déterministe — pas de LLM."""
    engine = MatchingEngine(mock_base_json)
    scraper_data = ScraperOutput(
        titre="Data Engineer",
        entreprise="Tech",
        description_clean="Python dev",
        mots_cles_detectes=["Python", "backend"],
        niveau_poste="Senior",
        probleme_detecte="N/A"
    )
    res = engine.process(scraper_data)
    assert res.persona_selectionne == "expert_python"
    assert res.score >= 60  # 2 mots matchés -> score >= 60
    assert res.next_action == "POSTULER"
    assert "Python" in res.mots_cles_ats

def test_matching_engine_score_all_personas(mock_base_json):
    """Test _score_all_personas — scoring déterministe par mots-clés."""
    engine = MatchingEngine(mock_base_json)
    scores = engine._score_all_personas(["Python", "backend", "API"])
    assert "expert_python" in scores
    assert scores["expert_python"]["score"] > 0
    assert "python" in scores["expert_python"]["matches"]  # intersection en lowercase

def test_matching_engine_detect_secteur():
    """Test _detect_secteur."""
    engine = MatchingEngine({"personas_specialises": {}})
    assert engine._detect_secteur("it_support_pme") == "it_support"
    assert engine._detect_secteur("vente_esn") == "vente"
    assert engine._detect_secteur("growth_seo_data_dev") == "growth_seo_data_dev"
