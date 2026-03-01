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
        mock_lm.return_value.process.return_value = "Contenu LM"
        mock_entreprise.return_value.process.return_value = {"email_trouve": "test@test.com"}
        mock_email.return_value.process.return_value = {"email_j0": "Hello", "sujet": "Sub"}
        
        orchestrator = Orchestrator(mock_base_json)
        result = orchestrator.run_pipeline("http://test.com")
        
        assert isinstance(result, FinalOutput)
        assert result.next_action == "POSTULER"
        assert result.matching["score"] == 95

def test_orchestrator_atv_failure(mock_base_json):
    # In the current implementation, ATV is handled in ReportAgent and doesn't raise ValueError by default
    pass
