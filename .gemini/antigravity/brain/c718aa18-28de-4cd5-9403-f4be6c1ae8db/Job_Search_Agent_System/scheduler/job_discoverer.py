"""
Découverte des offres par source — WTTJ (Playwright SPA), France Travail (requests).
URLs configurables — pas d'URL unique hardcodée.
"""
import random
import time
from typing import Any

import requests
from bs4 import BeautifulSoup

SOURCES: dict[str, dict[str, Any]] = {
    "wttj": {
        "queries": ["growth engineer", "developpeur python", "automatisation"],
        "base": "https://www.welcometothejungle.com",
    },
    "francetravail": {
        "urls": [
            "https://candidat.francetravail.fr/offres/recherche?motsCles=growth+engineer",
            "https://candidat.francetravail.fr/offres/recherche?motsCles=developpeur+python",
        ],
        "base": "https://candidat.francetravail.fr",
    },
    "indeed": {
        "base": "https://fr.indeed.com",
        "url_tpl": "https://fr.indeed.com/jobs?q={query}&l=France",
    },
    "hellowork": {
        "base": "https://www.hellowork.com",
        "urls": [
            "https://www.hellowork.com/fr-fr/emploi/metier_developpeur-informatique.html",
            "https://www.hellowork.com/fr-fr/emploi/metier_ingenieur.html",
            "https://www.hellowork.com/fr-fr/emploi/mot-cle_cdi.html",
        ],
    },
    "dogfinance": {
        "base": "https://dogfinance.com",
        "url_tpl": "https://dogfinance.com/en/offres?page={page}",
    },
    "meteojob": {
        "base": "https://www.meteojob.com",
        "urls": [
            "https://www.meteojob.com/jobs",
            "https://www.meteojob.com/Emploi-developpeur",
        ],
    },
    "glassdoor": {
        "base": "https://www.glassdoor.com",
        "url_tpl": "https://www.glassdoor.com/Job/france-{query}-jobs-SRCH_IL.0,6_IN86.htm",
    },
    "linkedin": {
        "base": "https://www.linkedin.com",
        "url_tpl": "https://www.linkedin.com/jobs/search/?keywords={query}&location=France",
    },
    "chooseyourboss": {
        "base": "https://www.chooseyourboss.com",
        "urls": [
            "https://www.chooseyourboss.com/offres/emploi-it",
        ],
    },
    "apec": {
        "base": "https://www.apec.fr",
        "urls": [
            "https://www.apec.fr/parcourir-les-emplois.html",
            "https://www.apec.fr/candidat/recherche-emploi.html/emploi?motsCles=developpeur+python",
            "https://www.apec.fr/candidat/recherche-emploi.html/emploi?motsCles=ingenieur",
        ],
    },
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}


def _discover_jobs_wttj_playwright(query: str, max_jobs: int) -> list[str]:
    """WTTJ SPA React — Playwright pour rendu JS."""
    from playwright.sync_api import sync_playwright

    url = f"https://www.welcometothejungle.com/fr/jobs?query={query.replace(' ', '+')}&page=1"
    urls: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # load au lieu de networkidle : évite blocage sur SPA avec polling infini
        page.goto(url, wait_until="load", timeout=25000)
        time.sleep(2)  # lazy load minimal

        links = page.query_selector_all("a[href*='/fr/companies/'][href*='/jobs/']")
        for link in links:
            href = link.get_attribute("href")
            if not href:
                continue
            path = href.split("?")[0].rstrip("/")
            if path.endswith("/jobs"):
                continue
            if "/fr/pages/" in href:
                continue
            if "/jobs/" not in path:
                continue
            job_slug = path.split("/jobs/", 1)[1].split("/")[0]
            if not job_slug:
                continue
            full = "https://www.welcometothejungle.com" + href if href.startswith("/") else href
            if full not in urls:
                urls.append(full)
            if len(urls) >= max_jobs:
                break

        browser.close()
    return urls


def _build_francetravail_urls(queries: list[str]) -> list[str]:
    """Construit les URLs France Travail depuis les requêtes."""
    base = SOURCES["francetravail"]["base"]
    return [f"{base}/offres/recherche?motsCles={q.replace(' ', '+')}" for q in queries]


def _discover_jobs_francetravail(max_jobs: int, base_json: dict | None = None) -> list[str]:
    """France Travail — requests + BeautifulSoup."""
    from scheduler.persona_queries import get_persona_queries

    urls: list[str] = []
    seen: set[str] = set()

    listing_urls = (
        _build_francetravail_urls(get_persona_queries(base_json, 2))
        if base_json
        else SOURCES["francetravail"]["urls"]
    )

    for listing_url in listing_urls:
        if len(urls) >= max_jobs:
            break
        try:
            time.sleep(random.uniform(2, 5))
            r = requests.get(listing_url, headers=HEADERS, timeout=15)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            links = soup.select("a[href*='/offres/recherche/detail/']")

            for a in links:
                href = a.get("href", "")
                if not href or href in seen:
                    continue
                base = SOURCES["francetravail"]["base"]
                full = base + href if href.startswith("/") else href
                seen.add(href)
                urls.append(full)
                if len(urls) >= max_jobs:
                    return urls
        except Exception as e:
            print(f"[discoverer] Erreur France Travail {listing_url} : {e}")

    return urls


def _discover_jobs_indeed(max_jobs: int, base_json: dict | None = None) -> list[str]:
    """Indeed France — requests + BeautifulSoup (peut 403 selon anti-bot)."""
    from scheduler.persona_queries import get_persona_queries

    queries = (
        get_persona_queries(base_json, max_per_persona=2)
        if base_json
        else ["developpeur python", "growth", "technicien support"]
    )
    urls: list[str] = []
    seen: set[str] = set()
    base = SOURCES["indeed"]["base"]
    tpl = SOURCES["indeed"]["url_tpl"]

    for q in queries[:4]:
        if len(urls) >= max_jobs:
            break
        url = tpl.format(query=q.replace(" ", "+"))
        try:
            time.sleep(random.uniform(2, 5))
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.select("a[href*='/rc/clk'], a[href*='/viewjob'], a[href*='/pagead/clk']"):
                href = a.get("href", "")
                if not href or "indeed.com" not in href:
                    continue
                full = base + href if href.startswith("/") else href
                if full not in seen:
                    seen.add(full)
                    urls.append(full)
                if len(urls) >= max_jobs:
                    return urls
        except Exception as e:
            print(f"[discoverer] Erreur Indeed {url[:60]} : {e}")

    return urls


def _discover_jobs_chooseyourboss(max_jobs: int, base_json: dict | None = None) -> list[str]:
    """ChooseYourBoss — requests + BeautifulSoup."""
    urls: list[str] = []
    seen: set[str] = set()
    base_site = SOURCES["chooseyourboss"]["base"]
    listing_urls = SOURCES["chooseyourboss"].get("urls", [f"{base_site}/offres/emploi-it"])

    for url in listing_urls:
        if len(urls) >= max_jobs:
            break
        try:
            time.sleep(random.uniform(2, 5))
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.select("a[href*='/candidates/offers/']"):
                href = a.get("href", "")
                if not href or href in seen:
                    continue
                if not href.startswith("http"):
                    full = base_site + href if href.startswith("/") else href
                else:
                    full = href
                seen.add(href)
                urls.append(full)
                if len(urls) >= max_jobs:
                    return urls
        except Exception as e:
            print(f"[discoverer] Erreur ChooseYourBoss : {e}")

    return urls


def _discover_jobs_hellowork(max_jobs: int, base_json: dict | None = None) -> list[str]:
    """HelloWork — requests + BeautifulSoup. Collecte uniquement /emplois/[id].html (offres individuelles)."""
    urls: list[str] = []
    seen: set[str] = set()
    base_site = SOURCES["hellowork"]["base"]
    listing_urls = SOURCES["hellowork"].get("urls", [])

    for url in listing_urls:
        if len(urls) >= max_jobs:
            break
        try:
            time.sleep(random.uniform(2, 5))
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.select("a[href*='/emplois/']"):
                href = a.get("href", "")
                if not href or href in seen:
                    continue
                full = base_site + href if href.startswith("/") else href
                if "/emplois/" in full and ".html" in full and full not in seen:
                    seen.add(href)
                    urls.append(full)
                if len(urls) >= max_jobs:
                    return urls
        except Exception as e:
            print(f"[discoverer] Erreur HelloWork : {e}")

    return urls[:max_jobs]


def _discover_jobs_dogfinance(max_jobs: int, base_json: dict | None = None) -> list[str]:
    """Dogfinance / emploi.agefi.fr — requests + BeautifulSoup."""
    urls: list[str] = []
    seen: set[str] = set()

    for page in range(1, 4):
        if len(urls) >= max_jobs:
            break
        try:
            time.sleep(random.uniform(2, 5))
            url = f"https://dogfinance.com/en/offres?page={page}"
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.select("a[href*='/offres/'], a[href*='emploi.agefi.fr'], a[href*='/offre/']"):
                href = a.get("href", "")
                if not href or href in seen:
                    continue
                if "offres?" in href or "page=" in href:
                    continue
                full = href if href.startswith("http") else f"https://emploi.agefi.fr{href}" if "agefi" in href else f"https://dogfinance.com{href}"
                seen.add(href)
                urls.append(full)
                if len(urls) >= max_jobs:
                    return urls
        except Exception as e:
            print(f"[discoverer] Erreur Dogfinance : {e}")

    return urls


def _discover_jobs_meteojob(max_jobs: int, base_json: dict | None = None) -> list[str]:
    """Meteojob — requests + BeautifulSoup."""
    urls: list[str] = []
    seen: set[str] = set()
    base_site = SOURCES["meteojob"]["base"]
    listing_urls = SOURCES["meteojob"].get("urls", ["https://www.meteojob.com/jobs"])

    for url in listing_urls:
        if len(urls) >= max_jobs:
            break
        try:
            time.sleep(random.uniform(2, 5))
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.select("a[href*='/emploi/'], a[href*='/Emploi/'], a[href*='/job/']"):
                href = a.get("href", "")
                if not href or href in seen:
                    continue
                full = base_site + href if href.startswith("/") else href
                if "meteojob.com" not in full:
                    continue
                seen.add(href)
                urls.append(full)
                if len(urls) >= max_jobs:
                    return urls
        except Exception as e:
            print(f"[discoverer] Erreur Meteojob : {e}")

    return urls


def _discover_jobs_glassdoor(max_jobs: int, base_json: dict | None = None) -> list[str]:
    """Glassdoor — requests + BeautifulSoup (peut bloquer)."""
    from scheduler.persona_queries import get_persona_queries

    queries = get_persona_queries(base_json, max_per_persona=2) if base_json else ["python", "developer", "data"]
    urls: list[str] = []
    seen: set[str] = set()
    tpl = SOURCES["glassdoor"]["url_tpl"]

    for q in queries[:3]:
        if len(urls) >= max_jobs:
            break
        try:
            time.sleep(random.uniform(3, 6))
            url = tpl.format(query=q.replace(" ", "-"))
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.select("a[href*='/Job/'], a[href*='job-listing']"):
                href = a.get("href", "")
                if not href or "glassdoor.com" not in href or href in seen:
                    continue
                if "jobs-SRCH" in href:
                    continue
                full = href if href.startswith("http") else "https://www.glassdoor.com" + href
                seen.add(href)
                urls.append(full)
                if len(urls) >= max_jobs:
                    return urls
        except Exception as e:
            print(f"[discoverer] Erreur Glassdoor : {e}")

    return urls


def _discover_jobs_linkedin(max_jobs: int, base_json: dict | None = None) -> list[str]:
    """LinkedIn Jobs — requests (très restrictif, peut 403). Playwright recommandé."""
    from scheduler.persona_queries import get_persona_queries

    queries = get_persona_queries(base_json, max_per_persona=2) if base_json else ["python", "developer"]
    urls: list[str] = []
    seen: set[str] = set()
    tpl = SOURCES["linkedin"]["url_tpl"]

    for q in queries[:3]:
        if len(urls) >= max_jobs:
            break
        try:
            time.sleep(random.uniform(3, 6))
            url = tpl.format(query=q.replace(" ", "+"))
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.select("a[href*='/jobs/view/'], a[href*='/job/']"):
                href = a.get("href", "")
                if not href or "linkedin.com" not in href or href in seen:
                    continue
                full = href.split("?")[0] if "?" in href else href
                if full not in seen:
                    seen.add(href)
                    urls.append(full)
                if len(urls) >= max_jobs:
                    return urls
        except Exception as e:
            print(f"[discoverer] Erreur LinkedIn : {e}")

    return urls


def _discover_jobs_apec(max_jobs: int, base_json: dict | None = None) -> list[str]:
    """APEC — offres emploi cadres. URLs /emploi/detail-offre/[id]."""
    from scheduler.persona_queries import get_persona_queries

    urls: list[str] = []
    seen: set[str] = set()
    base_site = SOURCES["apec"]["base"]
    listing_urls = SOURCES["apec"].get("urls", [])

    if base_json:
        queries = get_persona_queries(base_json, max_per_persona=2)
        listing_urls = [
            f"{base_site}/candidat/recherche-emploi.html/emploi?motsCles={q.replace(' ', '+')}"
            for q in queries[:3]
        ]

    for url in listing_urls:
        if len(urls) >= max_jobs:
            break
        try:
            time.sleep(random.uniform(2, 5))
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.select("a[href*='/detail-offre/']"):
                href = a.get("href", "")
                if not href or href in seen:
                    continue
                full = base_site + href if href.startswith("/") else href
                if full not in seen:
                    seen.add(href)
                    urls.append(full)
                if len(urls) >= max_jobs:
                    return urls
        except Exception as e:
            print(f"[discoverer] Erreur APEC : {e}")

    return urls


def discover_jobs(
    source: str,
    max_jobs: int = 10,
    base_json: dict | None = None,
) -> list[str]:
    """
    Retourne une liste d'URLs d'offres individuelles.
    Si base_json fourni : requêtes dérivées des personas (persona_queries).
    Sinon : requêtes SOURCES par défaut.
    WTTJ : Playwright (SPA React). France Travail : requests.
    """
    from scheduler.persona_queries import get_persona_queries

    source = source.strip().lower()
    config = SOURCES.get(source)
    if not config:
        raise ValueError(f"Source inconnue : {source}")

    queries = (
        get_persona_queries(base_json, max_per_persona=3)
        if base_json
        else config.get("queries", ["python"])
    )

    if source == "wttj":
        all_urls: list[str] = []
        seen: set[str] = set()
        for query in queries:
            if len(all_urls) >= max_jobs:
                break
            time.sleep(random.uniform(2, 5))
            batch = _discover_jobs_wttj_playwright(query, max_jobs - len(all_urls))
            for u in batch:
                if u not in seen:
                    seen.add(u)
                    all_urls.append(u)
        return all_urls[:max_jobs]

    if source == "francetravail":
        return _discover_jobs_francetravail(max_jobs, base_json)

    if source == "indeed":
        return _discover_jobs_indeed(max_jobs, base_json)

    if source == "chooseyourboss":
        return _discover_jobs_chooseyourboss(max_jobs, base_json)

    if source == "hellowork":
        return _discover_jobs_hellowork(max_jobs, base_json)

    if source == "dogfinance":
        return _discover_jobs_dogfinance(max_jobs, base_json)

    if source == "meteojob":
        return _discover_jobs_meteojob(max_jobs, base_json)

    if source == "glassdoor":
        return _discover_jobs_glassdoor(max_jobs, base_json)

    if source == "linkedin":
        return _discover_jobs_linkedin(max_jobs, base_json)

    if source == "apec":
        return _discover_jobs_apec(max_jobs, base_json)

    return []
