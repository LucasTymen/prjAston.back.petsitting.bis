import pytest
from core.compiler import OutputCompiler
from core.models import FinalOutput

def test_compiler_valid_data():
    compiler = OutputCompiler()
    valid_data = {
        "offre": {"titre": "T"},
        "matching": {"score": 100},
        "documents": {"cv": "cv.pdf", "lm": "lm.pdf"},
        "canal_application": {"canal": "email"},
        "email_trouve": {"contact": "test@test.com"},
        "next_action": "Envoyer email",
        "date_relance_j2": "2024-01-03",
        "date_relance_j4": "2024-01-05",
        "date_relance_j7": "2024-01-08",
        "date_relance_j9": "2024-01-10",
        "ATV_CHECK": {"donnees_verifiees": True, "hallucination_detectee": False, "commentaire": "OK"}
    }
    result = compiler.process(valid_data)
    assert result['next_action'] == "Envoyer email"

def test_compiler_invalid_data():
    compiler = OutputCompiler()
    invalid_data = {"offre": {}} # Manque plein de champs obligatoires
    with pytest.raises(ValueError):
        compiler.process(invalid_data)
