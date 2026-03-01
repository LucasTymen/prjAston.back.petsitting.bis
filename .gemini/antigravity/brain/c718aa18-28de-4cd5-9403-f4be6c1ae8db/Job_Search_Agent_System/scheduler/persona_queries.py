"""
Requêtes de découverte dérivées des personas (strategie_secteur ou personas_specialises).
Compatible Mistral Job Hunter / SquidResearch — queries alignées sur detection_mots_cles.
"""
from typing import Any


# Mapping persona → requêtes prioritaires (phrases WTTJ / France Travail compatibles)
# Fallback si le JSON n'a pas assez de mots-clés exploitables
DORKS_MISTRAL: dict[str, list[str]] = {
    "it_support": [
        "technicien support",
        "support N2",
        "helpdesk",
        "GLPI",
        "administrateur systèmes",
        "support informatique PME",
    ],
    "growth_seo_data_dev": [
        "growth engineer",
        "developpeur python",
        "backend",
        "automatisation",
        "SEO",
    ],
    "vente": [
        "commercial",
        "chef de rayon",
        "vente retail",
    ],
}


def get_persona_queries(base_json: dict, max_per_persona: int = 2) -> list[str]:
    """
    Extrait les requêtes de recherche depuis les personas du JSON.
    Priorité : strategie_secteur > personas_specialises > DORKS_MISTRAL.
    Retourne une liste de requêtes uniques (pour WTTJ query= ou France Travail motsCles=).
    """
    personas = base_json.get("meta", {}).get("strategie_secteur") or base_json.get(
        "personas_specialises", {}
    )
    if not isinstance(personas, dict):
        return _fallback_queries()

    queries: list[str] = []
    seen: set[str] = set()

    for persona_name, data in personas.items():
        if not isinstance(data, dict):
            continue
        mots = data.get("detection_mots_cles") or data.get("mots_cles_detection")
        if not mots or not isinstance(mots, list):
            # Fallback Mistral
            fallback = DORKS_MISTRAL.get(persona_name, [])
            for q in fallback[:max_per_persona]:
                if q not in seen:
                    seen.add(q)
                    queries.append(q)
            continue

        # Construire des requêtes exploitables (phrases 2 mots ou 1 mot)
        mots_clean = [str(m).strip() for m in mots[:8] if m]
        added = 0
        for i, m in enumerate(mots_clean[:6]):
            if added >= max_per_persona:
                break
            if not m or m in seen:
                continue
            # Préférer combo 2 mots si disponible
            if i + 1 < len(mots_clean) and mots_clean[i + 1]:
                combo = f"{m} {mots_clean[i + 1]}"
                if combo not in seen and len(combo) < 50:
                    seen.add(combo)
                    queries.append(combo)
                    added += 1
            if m not in seen and added < max_per_persona:
                seen.add(m)
                queries.append(m)
                added += 1

    if not queries:
        return _fallback_queries()
    return queries[:15]  # Limite raisonnable


def _fallback_queries() -> list[str]:
    """Requêtes par défaut (aligned Mistral / SquidResearch)."""
    return [
        "growth engineer",
        "developpeur python",
        "technicien support",
        "backend",
        "automatisation",
    ]
