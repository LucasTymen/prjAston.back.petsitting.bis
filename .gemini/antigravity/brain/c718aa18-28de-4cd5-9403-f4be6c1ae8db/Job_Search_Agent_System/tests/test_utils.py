"""Tests pour core.utils (sanitization placeholders, nommage pièces jointes)."""
import pytest
from core.utils import sanitize_placeholders, attachment_filenames


def test_sanitize_placeholders_substitutes_and_removes_unknown():
    text = "Candidature - {{titre_poste}} | {{prenom_recruteur}}"
    out = sanitize_placeholders(text, titre_poste="SOE technique", prenom_recruteur="Marie")
    assert "{{" not in out and "}}" not in out
    assert "SOE technique" in out
    assert "Marie" in out


def test_sanitize_placeholders_missing_value_becomes_empty():
    text = "Sujet : {{titre_poste}}"
    out = sanitize_placeholders(text, titre_poste="")
    assert "{{" not in out
    assert out.strip() == "Sujet :" or "Sujet" in out


def test_sanitize_placeholders_unknown_placeholder_removed():
    text = "Bonjour {{inconnu}} monde"
    out = sanitize_placeholders(text)
    assert "{{inconnu}}" not in out
    assert "Bonjour" in out and "monde" in out


def test_attachment_filenames_charter():
    cv_name, lm_name = attachment_filenames("Orange Travel", "SOE technique")
    assert cv_name.startswith("CV_Lucas_Tymen_")
    assert lm_name.startswith("LM_Lucas_Tymen_")
    assert "Orange" in cv_name or "orange" in cv_name.lower()
    assert "SOE" in cv_name or "soe" in cv_name.lower()
    assert cv_name.endswith(".pdf") and lm_name.endswith(".pdf")
