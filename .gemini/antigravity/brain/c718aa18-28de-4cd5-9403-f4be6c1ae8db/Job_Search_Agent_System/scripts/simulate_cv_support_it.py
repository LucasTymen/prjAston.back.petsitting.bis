"""
Simulation d'une candidature type "Technicien Support IT Anglais Bilingue"
pour comparer le CV généré à l'exemple de référence (TOG SUPPIT 0226 - Groupe GR).
Usage: python -m scripts.simulate_cv_support_it
"""
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.models import MatchingOutput
from agents.generator import CvAtvGenerator


def main():
    base_path = PROJECT_ROOT / "resources" / "base_real.json"
    if not base_path.exists():
        print("base_real.json introuvable, utilisation base.json")
        base_path = PROJECT_ROOT / "resources" / "base.json"
    with open(base_path, "r", encoding="utf-8") as f:
        base_json = json.load(f)

    # Offre équivalente à l'exemple (TOG SUPPIT 0226 - Groupe GR)
    offre = {
        "titre": "Technicien Support IT Anglais Bilingue",
        "entreprise": "Groupe GR",
        "reference": "TOG SUPPIT 0226",
    }

    # Matching type it_support (persona it_support_pme, mots-clés orientés support)
    match_data = MatchingOutput(
        persona_selectionne="Technicien Support Confirmé – Référent IT PME & Multisite",
        secteur_detecte="it_support",
        exposition_seniorite="Operationnelle",
        score=85,
        next_action="POSTULER",
        arguments_actives=["it_pme"],
        mots_cles_ats=[
            "Support N1 N2",
            "Microsoft 365",
            "Windows 10 11",
            "Active Directory",
            "GLPI",
            "ITSM",
            "Gestion parc",
            "Multisite",
            "Anglais opérationnel",
        ],
    )

    gen = CvAtvGenerator(base_json)
    cv_data = gen.process(match_data, offre=offre)
    cv_markdown = gen.render_cv_markdown(cv_data, offre=offre, final=True)

    # Sauvegarde pour comparaison
    out_path = PROJECT_ROOT / "outputs" / "cv_simule_support_it.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(cv_markdown)
    print("CV genere (simulation Technicien Support IT) ->", str(out_path))


if __name__ == "__main__":
    main()
