"""
Tests de régression sprint corrections — draft guard, EmailEngine fallback, bullet_cv.
"""
import pytest
from unittest.mock import MagicMock
from agents.drafting import GmailDraftingAgent
from agents.generator import CvAtvGenerator, EmailEngine
from core.models import MatchingOutput


def test_drafting_refuse_email_vide():
    """create_draft doit refuser to_email vide (sprint correction #4)."""
    agent = GmailDraftingAgent()
    result = agent.create_draft("", "Sujet", "Corps")
    assert result is False
    result2 = agent.create_draft(None, "Sujet", "Corps")
    assert result2 is False


def test_email_engine_fallback_dict():
    """EmailEngine doit retourner un dict avec clés fallback si LLM échoue (sprint #5)."""
    base = {"meta": {}, "experiences": [], "arguments_reutilisables": {}}
    match = MatchingOutput(
        persona_selectionne="test",
        secteur_detecte="growth_seo_data_dev",
        exposition_seniorite="Operationnelle",
        score=60,
        next_action="POSTULER",
        arguments_actives=[],
        mots_cles_ats=[],
    )
    eng = EmailEngine(base)
    eng.llm = MagicMock()
    eng.llm.chat_completion.return_value = None
    res = eng.process(match, offre={"titre": "Dev"})
    assert isinstance(res, dict)
    assert "sujet" in res
    assert "email_j0" in res


@pytest.fixture
def mock_base_json():
    return {"meta": {}, "experiences": [], "arguments_reutilisables": {}, "formations": [], "langues": []}


def test_cv_bullet_dict_fallback(mock_base_json):
    """bullet_cv_court dict avec structure atypique ne doit pas crasher (sprint #6)."""
    base = {
        **mock_base_json,
        "experiences": [{
            "entite": "X",
            "role": "Dev",
            "periode": "2020",
            "bullet_cv_court": {"autre_cle": "Point unique"},
        }],
        "formations": [],
        "langues": [],
        "narratifs_candidature": {"growth_seo_data_dev": "Profil"},
    }
    gen = CvAtvGenerator(base)
    match = MatchingOutput(
        persona_selectionne="backend_django",
        secteur_detecte="growth_seo_data_dev",
        exposition_seniorite="Operationnelle",
        score=60,
        next_action="POSTULER",
        arguments_actives=[],
        mots_cles_ats=[],
    )
    cv_data = gen.process(match)
    assert "experiences" in cv_data
    assert len(cv_data["experiences"]) >= 1
    bullets = cv_data["experiences"][0].get("bullets", [])
    assert isinstance(bullets, list)
