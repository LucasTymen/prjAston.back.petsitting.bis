"""
File d'offres à traiter — découverte par source + itération.
Additive : ne modifie pas les agents existants.
"""
import logging
from typing import Iterator
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

log = logging.getLogger("job_queue")

# Patterns de liens pour extraire les URLs d'offres par source
SOURCES = {
    "wttj": {
        "url": "https://www.welcometothejungle.com/fr/jobs",
        "link_patterns": ("/fr/companies/", "/fr/jobs/"),
        "base_url": "https://www.welcometothejungle.com",
    },
    "linkedin": {
        "url": "https://www.linkedin.com/jobs/search/",
        "link_patterns": ("/jobs/view/",),
        "base_url": "https://www.linkedin.com",
    },
    "indeed": {
        "url": "https://fr.indeed.com/jobs",
        "link_patterns": ("/jobs?", "/rc/clk?"),
        "base_url": "https://fr.indeed.com",
    },
}


class JobQueue:
    """
    File en mémoire des offres à traiter lors d'un run cron.
    discover() récupère les URLs depuis une page de recherche.
    """

    def __init__(self) -> None:
        self._pending: list[str] = []

    def discover(self, source_url: str, source_key: str | None = None) -> list[str]:
        """
        Découvre les URLs d'offres depuis une page de recherche.
        Retourne [] en cas d'erreur — fail-safe, ne casse pas le pipeline.
        """
        try:
            response = requests.get(source_url, timeout=15)
            response.raise_for_status()
        except requests.RequestException as e:
            log.warning("Erreur fetch %s : %s", source_url[:60], e)
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        config = SOURCES.get(source_key or "wttj", SOURCES["wttj"])
        patterns = config["link_patterns"]
        base = config.get("base_url", urlparse(source_url).netloc or "https://" + urlparse(source_url).netloc)

        seen: set[str] = set()
        urls: list[str] = []

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not any(p in href for p in patterns):
                continue
            full = urljoin(base if href.startswith("/") else source_url, href)
            # Nettoyer fragment et query pour dédup interne
            parsed = urlparse(full)
            clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if clean not in seen:
                seen.add(clean)
                urls.append(clean)

        return urls[:50]  # Limite raisonnable par run

    def add(self, url: str) -> None:
        if url and url not in self._pending:
            self._pending.append(url)

    def iter_pending(self) -> Iterator[str]:
        while self._pending:
            yield self._pending.pop(0)
