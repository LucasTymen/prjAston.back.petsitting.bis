"""
Tests data-driven pour le MatchingEngine — benchmarks de correction.
Charge les cas depuis tests/benchmark_data/matching_cases.json.
"""
import json
from pathlib import Path

import pytest
from core.models import ScraperOutput
from agents.matching import MatchingEngine

BENCHMARK_DIR = Path(__file__).resolve().parent / "benchmark_data"


def _load_base_json():
    """Charge base_real.json ou fallback minimal avec personas."""
    base_path = Path(__file__).resolve().parent.parent / "resources" / "base_real.json"
    if base_path.exists():
        return json.loads(base_path.read_text(encoding="utf-8"))
    # Fallback minimal pour CI
    return {
        "personas_specialises": {
            "seo_technique": {
                "mots_cles_detection": ["SEO", "technique", "GA4", "GTM"],
                "arguments_prioritaires": [],
            },
            "automation_engineer": {
                "mots_cles_detection": ["automation", "pipeline", "data", "Big data", "IA", "machine learning", "ML"],
                "arguments_prioritaires": [],
            },
        },
        "persona_engine": {"poids_par_type": {"competence_technique": 3}},
    }


@pytest.fixture
def base_json():
    return _load_base_json()


def _load_benchmark_cases():
    path = BENCHMARK_DIR / "matching_cases.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", _load_benchmark_cases(), ids=lambda c: c.get("id", ""))
def test_matching_benchmark_case(base_json, case):
    """Test data-driven : chaque cas du benchmark doit passer."""
    so = case["scraper_output"]
    # Pydantic accepte None pour niveau_poste si le modèle le permet ; ScraperOutput a niveau_poste: str
    niveau = so.get("niveau_poste")
    if niveau is None:
        niveau = ""
    scraper_data = ScraperOutput(
        titre=so.get("titre", ""),
        entreprise=so.get("entreprise", ""),
        description_clean=so.get("description_clean", ""),
        mots_cles_detectes=so.get("mots_cles_detectes", []),
        niveau_poste=niveau,
        probleme_detecte=so.get("probleme_detecte", "N/A"),
    )
    engine = MatchingEngine(base_json)
    result = engine.process(scraper_data)

    expected = case.get("expected", {})
    if expected.get("no_crash"):
        assert result is not None
    if "exposition_seniorite" in expected:
        assert result.exposition_seniorite == expected["exposition_seniorite"]
    if "persona_selectionne" in expected:
        assert result.persona_selectionne == expected["persona_selectionne"]
    if "score_min" in expected:
        assert result.score >= expected["score_min"]


def test_matching_niveau_poste_none_no_crash(base_json):
    """Régression : niveau_poste None ne doit pas lever AttributeError."""
    engine = MatchingEngine(base_json)
    scraper_data = ScraperOutput(
        titre="Test",
        entreprise="X",
        description_clean="",
        mots_cles_detectes=[],
        niveau_poste="",
        probleme_detecte="",
    )
    res = engine.process(scraper_data)
    assert res.exposition_seniorite in ("Operationnelle", "Strategique")


def test_matching_expand_keywords(base_json):
    """SEO technique -> tokens seo, technique pour matching."""
    engine = MatchingEngine(base_json)
    expanded = engine._expand_keywords(["SEO technique", "Big data"])
    assert "seo" in expanded
    assert "technique" in expanded
    assert "big" in expanded
    assert "data" in expanded
