import pytest
import os
import shutil
from unittest.mock import MagicMock, patch
from agents.matching import MatchingEngine
from agents.generator import CvAtvGenerator
from agents.drafting import GmailDraftingAgent
from agents.cv_pdf import CvPdfGenerator
from agents.scraper import ScraperOffre
from core.llm_client import OpenAIClient
from core.orchestrator import Orchestrator
from core.models import MatchingOutput

# Final coverage gap push — MatchingEngine déterministe (pas de cosine_similarity)
def test_matching_score_all_personas():
    engine = MatchingEngine({
        "personas_specialises": {"p1": {"mots_cles_detection": ["a", "b"], "arguments_prioritaires": []}},
        "persona_engine": {},
    })
    scores = engine._score_all_personas(["a", "b"])
    assert "p1" in scores
    assert scores["p1"]["score"] > 0
    assert len(scores["p1"]["matches"]) == 2

def test_matching_detect_secteur():
    engine = MatchingEngine({})
    assert engine._detect_secteur("it_support_pme") == "it_support"
    assert engine._detect_secteur("vente") == "vente"

def test_generator_bullets_fallback():
    generator = CvAtvGenerator({"meta": {}, "experiences": [{"entite": "T", "bullet_cv_court": {"version_operationnelle": ["Op"]}}]})
    res = generator.process(MatchingOutput(persona_selectionne="p", secteur_detecte="s", exposition_seniorite="Operationnelle", score=0, next_action="a", arguments_actives=[], mots_cles_ats=[]))
    assert res["experiences"][0]["bullets"] == ["Op"]
    
    # Test line 42 fallback
    generator.base_json["experiences"] = [{"entite": "T", "bullet_cv_court": "not a list or dict"}]
    res = generator.process(MatchingOutput(persona_selectionne="p", secteur_detecte="s", exposition_seniorite="Operationnelle", score=0, next_action="a", arguments_actives=[], mots_cles_ats=[]))
    assert res["experiences"][0]["bullets"] == []

@patch("core.llm_client.OpenAI")
def test_llm_client_full(mock_openai):
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test"}):
        client = OpenAIClient()
        mock_openai.return_value.chat.completions.create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content='{"k":"v"}'))])
        client.chat_completion("h")
        
    with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=True):
        with pytest.raises(ValueError):
            OpenAIClient()

@patch("agents.drafting.imaplib.IMAP4_SSL")
def test_gmail_drafting_folders(mock_imap):
    with patch.dict(os.environ, {"GMAIL_USER": "u", "GMAIL_APP_PASSWORD": "p"}):
        agent = GmailDraftingAgent()
        mock_imap_instance = mock_imap.return_value
        # Coverage for line 56-59 (split logic)
        mock_imap_instance.list.return_value = ("OK", [b'(\\HasNoChildren) "/" "[Gmail]/Drafts"'])
        agent.create_draft("to", "sub", "body")
        
def test_scraper_full():
    scraper = ScraperOffre()
    url = "https://www.hellowork.com/fr-fr/emplois/24032203.html"
    scraper.extract_with_llm(url, "text")

def test_cv_pdf_full():
    test_dir = "C:\\tmp\\test_cvs_new"
    if os.path.exists(test_dir): shutil.rmtree(test_dir)
    gen = CvPdfGenerator(test_dir)
    # Test line 34-37 indirectly via generate
    with patch("agents.cv_pdf.SimpleDocTemplate") as mock_doc:
        gen.generate("t.pdf", {"nom": "n", "experiences": [{"entite": "e", "bullets": ["b"]}]})
        assert mock_doc.called

def test_orchestrator_success_branch():
    with patch('core.orchestrator.ScraperOffre') as mock_scraper, \
         patch('core.orchestrator.MatchingEngine') as mock_matching, \
         patch('core.orchestrator.CvAtvGenerator') as mock_cv, \
         patch('core.orchestrator.LmCoordinator') as mock_lm, \
         patch('core.orchestrator.EmailEngine') as mock_email, \
         patch('core.orchestrator.EntrepriseScraper') as mock_entreprise, \
         patch('core.orchestrator.GmailDraftingAgent') as mock_draft:
        
        mock_matching.return_value.process.return_value = MatchingOutput(
            persona_selectionne="p", secteur_detecte="s", exposition_seniorite="e", 
            score=90, next_action="POSTULER", arguments_actives=[], mots_cles_ats=[]
        )
        mock_scraper.return_value.process.return_value = MagicMock()
        mock_scraper.return_value.process.return_value.model_dump.return_value = {"t":"t"}
        mock_entreprise.return_value.process.return_value = {"email_trouve": "test@test.com"}
        mock_email.return_value.process.return_value = {"email_j0": "hi", "sujet": "s"}
        mock_cv.return_value.process.return_value = {"nom": "n"}
        mock_lm.return_value.process.return_value = "LM"
        mock_draft.return_value.create_draft.return_value = True # Line 89 success
        
        orch = Orchestrator({"meta": {"nom": "n"}})
        orch.run_pipeline("url", create_draft=True)
        assert mock_draft.return_value.create_draft.called
