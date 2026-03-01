"""
Export JobScanner 24h — CSV ou JSON.
CSV : colonnes date_scan,titre,entreprise,source,localisation,secteur,persona,score_pct,
      type_metier,exposition_seniorite,recommandation,lien[, top_keywords_detected]
JSON : objet avec metadata + offres (liste d’objets).
"""
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Mapping persona/secteur -> type_metier JobScanner
TYPE_METIER = {
    "it_support": "IT Support",
    "it_support_pme": "IT Support",
    "growth_seo_data_dev": "Automation/Data",
    "backend_django": "Backend Django",
    "growth_ops": "Growth Ops",
    "vente": "Hybride",
}


def recommandation_jobscanner(score: int) -> str:
    """JobScanner seuils : >=75 POSTULER, 60-74 À analyser, 45-59 Opportunité secondaire, <45 PASSER."""
    if score >= 75:
        return "POSTULER"
    if score >= 60:
        return "À analyser"
    if score >= 45:
        return "Opportunité secondaire"
    return "PASSER"


def _persona_to_type_metier(persona: str, secteur: str) -> str:
    return TYPE_METIER.get(persona or "", None) or TYPE_METIER.get(secteur or "", "Hybride")


def build_scan_record(
    titre: str,
    entreprise: str,
    source: str,
    localisation: str,
    secteur: str,
    persona: str,
    score_pct: int,
    exposition_seniorite: str,
    recommandation: str,
    lien: str,
    top_keywords: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Construit un enregistrement JobScanner (réutilisable CSV/JSON)."""
    type_metier = _persona_to_type_metier(persona, secteur)
    date_scan = datetime.now().strftime("%Y-%m-%d")
    exp = exposition_seniorite.lower() if exposition_seniorite else "operationnelle"
    rec: Dict[str, Any] = {
        "date_scan": date_scan,
        "titre": titre,
        "entreprise": entreprise,
        "source": source,
        "localisation": localisation or "",
        "secteur": secteur or "growth_seo_data_dev",
        "persona": persona or "growth_seo_data_dev",
        "score_pct": score_pct,
        "type_metier": type_metier,
        "exposition_seniorite": exp,
        "recommandation": recommandation,
        "lien": lien,
    }
    if top_keywords:
        rec["top_keywords_detected"] = top_keywords[:5]
    return rec


def append_scan_line(
    path: Union[Path, str],
    titre: str,
    entreprise: str,
    source: str,
    localisation: str,
    secteur: str,
    persona: str,
    score_pct: int,
    exposition_seniorite: str,
    recommandation: str,
    lien: str,
    top_keywords: Optional[List[str]] = None,
) -> None:
    """Ajoute une ligne au CSV JobScanner. Crée le fichier + header si absent."""
    rec = build_scan_record(
        titre, entreprise, source, localisation, secteur, persona,
        score_pct, exposition_seniorite, recommandation, lien, top_keywords,
    )
    if top_keywords and "top_keywords_detected" in rec:
        rec["top_keywords_detected"] = "|".join(rec["top_keywords_detected"])
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists()
    fieldnames = list(rec.keys())
    row = rec
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            w.writeheader()
        w.writerow(row)


def write_scan_json(path: Union[Path, str], records: List[Dict[str, Any]], sources: Optional[List[str]] = None) -> None:
    """Écrit un fichier JSON JobScanner : metadata + offres."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "metadata": {
            "date_scan": datetime.now().strftime("%Y-%m-%d"),
            "sources": sources or [],
            "nombre_offres": len(records),
        },
        "offres": records,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
