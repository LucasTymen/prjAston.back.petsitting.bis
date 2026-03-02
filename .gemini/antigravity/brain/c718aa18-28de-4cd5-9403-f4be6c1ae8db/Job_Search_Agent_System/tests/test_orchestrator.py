import pytest
from unittest.mock import MagicMock, patch
from core.orchestrator import Orchestrator
from core.models import ScraperOutput, MatchingOutput, FinalOutput

@pytest.fixture
def mock_base_json():
    return {"meta": {"nom": "Test"}, "experiences": []}

def test_orchestrator_run_pipeline_success(mock_base_json):
    with patch('core.orchestrator.ScraperOffre') as mock_scraper, \
         patch('core.orchestrator.MatchingEngine') as mock_matching, \
         patch('core.orchestrator.CvAtvGenerator') as mock_cv, \
         patch('core.orchestrator.LmCoordinator') as mock_lm, \
         patch('core.orchestrator.EmailEngine') as mock_email, \
         patch('core.orchestrator.EntrepriseScraper') as mock_entreprise:
        
        # Setup mock returns
        mock_match_obj = MatchingOutput(
            persona_selectionne="backend_django",
            secteur_detecte="growth_seo_data_dev",
            exposition_seniorite="Strategique",
            score=95,
            next_action="POSTULER",
            arguments_actives=["Arg1"],
            mots_cles_ats=["Django"]
        )
        
        mock_scraper_data = ScraperOutput(
            titre="Job",
            entreprise="Company",
            description_clean="Desc",
            mots_cles_detectes=["Python"],
            niveau_poste="Senior",
            probleme_detecte="None"
        )
        
        mock_scraper.return_value.process.return_value = mock_scraper_data
        mock_matching.return_value.process.return_value = mock_match_obj
        mock_cv.return_value.process.return_value = {"nom": "Test"}
        mock_cv.return_value.render_cv_markdown.return_value = "CV markdown"
        mock_lm.return_value.process.return_value = "Contenu LM"
        mock_entreprise.return_value.process.return_value = {"email_trouve": "test@test.com"}
        mock_email.return_value.process.return_value = {"email_j0": "Hello", "sujet": "Sub"}
        
        orchestrator = Orchestrator(mock_base_json)
        result = orchestrator.run_pipeline("http://test.com")
        
        assert isinstance(result, FinalOutput)
        assert result.next_action == "POSTULER"
        assert result.matching["score"] == 95

def test_orchestrator_atv_check(mock_base_json):
    """ATV_CHECK reflète la validation réelle (sprint correction #1)."""
    with patch('core.orchestrator.ScraperOffre') as mock_scraper, \
         patch('core.orchestrator.MatchingEngine') as mock_matching, \
         patch('core.orchestrator.CvAtvGenerator') as mock_cv, \
         patch('core.orchestrator.LmCoordinator') as mock_lm, \
         patch('core.orchestrator.EmailEngine') as mock_email, \
         patch('core.orchestrator.EntrepriseScraper') as mock_entreprise:
        mock_match = MagicMock()
        mock_match.model_dump.return_value = {"score": 90, "persona_selectionne": "x"}
        mock_match.next_action = "POSTULER"
        mock_matching.return_value.process.return_value = mock_match
        mock_scraper.return_value.process.return_value = MagicMock(
            titre="J", entreprise="C", description_clean="", mots_cles_detectes=[],
            niveau_poste="", probleme_detecte="", model_dump=lambda: {}
        )
        mock_cv.return_value.process.return_value = {"nom": "Test"}
        mock_cv.return_value.render_cv_markdown.return_value = "CV sans chiffres"
        mock_lm.return_value.process.return_value = "LM sans chiffres"
        mock_entreprise.return_value.process.return_value = {}
        mock_email.return_value.process.return_value = {"sujet": "S", "email_j0": "B"}

        orch = Orchestrator(mock_base_json)
        result = orch.run_pipeline("http://x.com")
        assert result.ATV_CHECK.donnees_verifiees is True
        assert result.ATV_CHECK.hallucination_detectee is False
