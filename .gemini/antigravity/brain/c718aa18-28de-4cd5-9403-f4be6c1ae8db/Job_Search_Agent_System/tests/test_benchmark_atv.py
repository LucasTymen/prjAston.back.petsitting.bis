"""
Tests data-driven pour la validation ATV — benchmarks anti-hallucination.
"""
import pytest
from core.atv_validator import valider_donnees


@pytest.fixture
def base_json_minimal():
    """Base JSON avec chiffres autorisés (908, 30, 1388, etc.)."""
    return {
        "meta": {"nom": "Test"},
        "experiences": [{"bullet_cv_court": ["908 leads", "30% tickets"]}],
        "preuves_business_contextualisees": [{"donnee_brute": "1388 req/s"}],
    }


def test_atv_ok_sans_chiffres(base_json_minimal):
    """Texte sans chiffres -> validation OK."""
    ok, msg = valider_donnees(base_json_minimal, "CV markdown sans chiffres")
    assert ok is True


def test_atv_ok_chiffres_autorisés(base_json_minimal):
    """Chiffres présents dans base -> validation OK."""
    ok, msg = valider_donnees(base_json_minimal, "908 leads qualifiés, réduction 30%")
    assert ok is True


def test_atv_fail_chiffre_inventé(base_json_minimal):
    """Chiffre absent de la base -> hallucination détectée."""
    ok, msg = valider_donnees(base_json_minimal, "150 leads par mois")
    assert ok is False
    assert "150" in msg or "hallucination" in msg.lower()
