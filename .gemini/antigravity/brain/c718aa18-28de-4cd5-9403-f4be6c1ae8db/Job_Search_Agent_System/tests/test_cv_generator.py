import pytest
from agents.generator import CvAtvGenerator
from core.models import MatchingOutput

@pytest.fixture
def mock_base_json():
    return {
        "meta": {
            "nom": "Lucas Tymen",
            "version": "2.4"
        },
        "experiences": [
            {
                "entite": "SquidResearch",
                "role": "Développeur Fullstack",
                "periode": "2024 - en cours",
                "bullet_cv_court": ["Bullet 1"],
                "priorite_secteur": {"it_support": "non pertinent"}
            },
            {
                "entite": "A.P.S.I.",
                "role_it": "Responsable IT",
                "periode_it": "2000–2022",
                "periode_growth": "2015–2022",
                "bullet_cv_court": {
                    "version_strategique": ["Bullet Strat"],
                    "version_operationnelle": ["Bullet Op"]
                },
                "priorite_secteur": {"it_support": "principale"}
            },
            {
                "entite": "Other",
                "periode": "1999-2000",
                "bullet_cv_court": None,
                "priorite_secteur": {"it_support": "secondaire"}
            }
        ]
    }

def test_cv_atv_generator_process(mock_base_json):
    generator = CvAtvGenerator(mock_base_json)
    match_data = MatchingOutput(
        persona_selectionne="backend_django",
        secteur_detecte="growth_seo_data_dev",
        exposition_seniorite="Strategique",
        score=85,
        next_action="POSTULER",
        arguments_actives=["Arg1"],
        mots_cles_ats=["Python"]
    )
    result = generator.process(match_data)
    assert isinstance(result, dict)
    assert result["nom"] == "Lucas Tymen"
    # Secteur growth : pas de filtre, exp[1] = A.P.S.I., periode_growth
    assert result["experiences"][1]["periode"] == "2015–2022"
    assert result["experiences"][1]["bullets"] == ["Bullet Strat"]

def test_cv_atv_generator_operationnelle(mock_base_json):
    generator = CvAtvGenerator(mock_base_json)
    match_data = MatchingOutput(
        persona_selectionne="technicien_it",
        secteur_detecte="it_support",
        exposition_seniorite="Operationnelle",
        score=85,
        next_action="POSTULER",
        arguments_actives=[],
        mots_cles_ats=[]
    )
    result = generator.process(match_data)
    # Secteur it_support : A.P.S.I. en tête, periode_it (2000–2022) pour les 22 ans
    assert result["experiences"][0]["periode"] == "2000–2022"
    assert result["experiences"][0]["bullets"] == ["Bullet Op"]

def test_cv_atv_generator_missing_fields(mock_base_json):
    generator = CvAtvGenerator(mock_base_json)
    match_data = MatchingOutput(
        persona_selectionne="unknown",
        secteur_detecte="it_support",
        exposition_seniorite="Operationnelle",
        score=0,
        next_action="PASSER",
        arguments_actives=[],
        mots_cles_ats=[]
    )
    result = generator.process(match_data)
    # it_support : filtre principale/secondaire → APSI (0) + Other (1) ; Other a bullets []
    assert result["experiences"][1]["bullets"] == []
