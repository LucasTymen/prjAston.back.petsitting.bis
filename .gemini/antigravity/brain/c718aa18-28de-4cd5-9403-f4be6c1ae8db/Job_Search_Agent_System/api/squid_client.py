"""
Client API SquidResearch — offer/submit pour enrichissement externe.
Compatible job-prospection-tool Mistral.
Usage : SQUID_API_URL + SQUID_API_TOKEN dans .env.
"""
import json
import os
from typing import Any

import requests


def offer_submit(
    url: str | None = None,
    texte_brut: str | None = None,
    source: str | None = None,
    secteur_suppose: str = "growth_seo_data_dev",
    base_url: str | None = None,
    token: str | None = None,
) -> dict[str, Any] | None:
    """
    POST /api/external-agents/v1/offer/submit/
    Args:
        url: URL de l'offre (priorité sur texte_brut)
        texte_brut: Texte brut de l'offre (si pas d'URL)
        source: Source du texte (optionnel)
        secteur_suppose: it_support | growth_seo_data_dev | vente
        base_url: https://api.squidresearch.fr ou http://127.0.0.1:8000
        token: Bearer token (header Authorization)
    Returns:
        data avec score, verdict, payload_campagne_comet, ou None si erreur
    """
    base = base_url or os.environ.get("SQUID_API_URL", "")
    tok = token or os.environ.get("SQUID_API_TOKEN", "")
    if not base or not tok:
        return None

    endpoint = base.rstrip("/") + "/api/external-agents/v1/offer/submit/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {tok}",
    }

    if url:
        payload = {"url": url, "secteur_suppose": secteur_suppose}
    elif texte_brut:
        payload = {
            "texte_brut": texte_brut,
            "source": source or "manual",
            "secteur_suppose": secteur_suppose,
        }
    else:
        return None

    try:
        r = requests.post(endpoint, json=payload, headers=headers, timeout=60)
        r.raise_for_status()
        data = r.json()
        return data.get("data") if data.get("success") else None
    except requests.RequestException:
        return None
