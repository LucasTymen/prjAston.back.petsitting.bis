"""
Tests pour le module LLM du chatbot (scheduler/chatbot_llm.py).
"""
import pytest
from scheduler.chatbot_llm import _get_raci_context


def test_get_raci_context_with_organisation():
    """RACI extrait depuis experiences[].realisation.organisation."""
    base = {
        "experiences": [
            {
                "realisation": {
                    "organisation": {
                        "methodologie": "Matrice RACI",
                        "raci": {
                            "expert_automatisation": {
                                "statut": "Expert IA",
                                "raci_role": "Exécutant (R)",
                            },
                            "chef_de_projet": {
                                "responsabilite": "Adaptation RACI",
                            },
                        },
                    },
                },
            },
        ],
    }
    ctx = _get_raci_context(base)
    assert "RACI" in ctx
    assert "expert_automatisation" in ctx
    assert "chef_de_projet" in ctx
    assert "Expert IA" in ctx


def test_get_raci_context_empty():
    """Sans organisation, retourne chaîne vide."""
    ctx = _get_raci_context({})
    assert ctx == ""
    ctx2 = _get_raci_context({"experiences": []})
    assert ctx2 == ""
