"""
Point d'entrée appelé par cron toutes les 2h.
Usage : python -m scheduler.cron_runner --sources wttj,francetravail --max 5

Utilise job_discoverer (URLs configurables) — pas d'URL hardcodée.
"""
import argparse
import json
import logging
from datetime import datetime
from pathlib import Path

from agents.scraper import ScraperOffre
from agents.matching import MatchingEngine
from core.orchestrator import Orchestrator
from core.models import FinalOutput
from scheduler.job_discoverer import discover_jobs
from scheduler.dedup import DedupStore
from storage.db import save_application

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STORAGE_DIR = PROJECT_ROOT / "storage"
LOGS_DIR = PROJECT_ROOT / "logs"
RESOURCES_DIR = PROJECT_ROOT / "resources"

LOGS_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "cron.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("cron_runner")


def _load_base_json() -> dict:
    """Charge le profil candidat — priorité cv_base, fallback base.json."""
    for name in ("cv_base_datas_pour_candidatures.json", "base.json"):
        path = RESOURCES_DIR / name
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    raise FileNotFoundError("Aucun profil trouvé dans resources/ (base.json ou cv_base_datas_pour_candidatures.json)")


def _save_output(result: FinalOutput, url: str) -> None:
    """Écrit le résultat JSON dans storage/outputs/."""
    slug = url.split("/")[-1][:40].replace("/", "-") or "output"
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    out_dir = STORAGE_DIR / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{slug}_{ts}.json"
    path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    log.info("Output écrit : %s", path)


def _ensure_personas(base_json: dict) -> dict:
    """Mappe strategie_secteur -> personas_specialises pour MatchingEngine."""
    strategie = base_json.get("meta", {}).get("strategie_secteur", {})
    if not strategie or base_json.get("personas_specialises"):
        return base_json
    personas = {
        k: {"mots_cles_detection": v.get("detection_mots_cles", []), "arguments_prioritaires": []}
        for k, v in strategie.items()
        if isinstance(v, dict)
    }
    return {**base_json, "personas_specialises": personas}


def run_both(
    sources: list[str],
    base_json: dict,
    max_jobs: int = 5,
    dry_run: bool = False,
) -> int:
    """
    Mode both corrigé :
    1. Scan -> découverte + matching -> liste des URLs POSTULER uniquement
    2. Pipeline full -> traite uniquement ces URLs
    Dedup partagé : on ne marque 'seen' qu'APRÈS le pipeline full (ou pour PASSER).
    """
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    dedup_path = STORAGE_DIR / "seen_jobs.db"
    dedup = DedupStore(str(dedup_path))
    base_with_personas = _ensure_personas(base_json)
    scraper = ScraperOffre()
    matching = MatchingEngine(base_with_personas)
    urls_to_process: list[tuple[str, object]] = []

    # Phase 1 — Scan et pré-filtrage
    for source in sources:
        source = source.strip().lower()
        log.info("Découverte : %s", source)
        try:
            urls = discover_jobs(source, base_json=base_json, max_jobs=max_jobs)
            log.info("%s - %d offres trouvées", source, len(urls))
        except ValueError as e:
            log.warning("%s", e)
            continue
        except Exception as e:
            log.error("Échec découverte %s : %s", source, e)
            continue

        for url in urls:
            if dedup.seen(url):
                log.debug("Déjà vu, skip : %s", url[:60])
                continue

            log.info("Scan : %s", url[:80])
            try:
                offre = scraper.process(url)
                match_data = matching.process(offre)

                if match_data.next_action == "POSTULER":
                    urls_to_process.append((url, match_data))
                    log.info("POSTULER — score=%s persona=%s — %s", match_data.score, match_data.persona_selectionne, url[:70])
                else:
                    log.info("PASSER — score=%s — %s", match_data.score, url[:70])
                    dedup.mark_seen(url)
            except Exception as e:
                log.error("Erreur scan %s : %s", url[:60], e)
                dedup.mark_failed(url, str(e))

    log.info("Scan terminé — %d offres POSTULER à traiter", len(urls_to_process))

    # Phase 2 — Pipeline complet uniquement sur POSTULER
    orchestrator = Orchestrator(base_json=base_json)
    total_processed = 0
    for url, _match_data in urls_to_process:
        try:
            if not dry_run:
                result = orchestrator.run_pipeline(url, create_draft=False)
                save_application(result, url, db_path=str(STORAGE_DIR))
                _save_output(result, url)
                log.info("Pipeline OK — %s", url[:70])
            else:
                log.info("[DRY RUN] Pipeline simulé pour %s", url[:60])
            dedup.mark_seen(url)
            total_processed += 1
        except Exception as e:
            log.error("Erreur pipeline %s : %s", url[:60], e)
            dedup.mark_failed(url, str(e))

    log.info("Run both terminé — %d offres traitées", total_processed)
    return total_processed


def run(
    sources: list[str],
    base_json: dict,
    dry_run: bool = False,
    max_per_source: int = 5,
) -> int:
    """
    Exécute un run cron : découverte (job_discoverer) → dedup → pipeline → persistance.
    Retourne le nombre d'offres traitées.
    """
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    dedup_path = STORAGE_DIR / "seen_jobs.db"
    dedup = DedupStore(str(dedup_path))
    orchestrator = Orchestrator(base_json=base_json)
    total_processed = 0

    for source in sources:
        source = source.strip().lower()
        log.info("Découverte : %s", source)
        try:
            job_urls = discover_jobs(
                source,
                max_jobs=max_per_source,
                base_json=base_json,
            )
            log.info("%s - %d offres trouvees", source, len(job_urls))
        except ValueError as e:
            log.warning("%s", e)
            continue
        except Exception as e:
            log.error("Échec découverte %s : %s", source, e)
            continue

        for url in job_urls:
            if dedup.seen(url):
                log.info("Déjà traitée, skip : %s", url[:70])
                continue

            log.info("Traitement : %s", url[:80])
            try:
                if dry_run:
                    log.info("[DRY RUN] Pipeline simulé pour %s", url[:60])
                    dedup.mark_seen(url)
                    total_processed += 1
                    continue

                result = orchestrator.run_pipeline(url, create_draft=False)
                save_application(result, url, db_path=str(STORAGE_DIR))
                _save_output(result, url)
                matching = result.matching or {}
                score = matching.get("score")
                persona = matching.get("persona_selectionne")
                log.info("OK — score=%s persona=%s action=%s", score, persona, result.next_action)
                dedup.mark_seen(url)
                total_processed += 1

            except Exception as e:
                log.error("Échec pipeline %s : %s", url[:60], e)
                dedup.mark_failed(url, str(e))

    log.info("Run terminé — %d offres traitées", total_processed)
    return total_processed


def main() -> None:
    parser = argparse.ArgumentParser(description="Cron runner Job Search Agent")
    parser.add_argument("--sources", default="wttj,francetravail,indeed,hellowork,dogfinance,meteojob,glassdoor,linkedin,apec",
                    help="Sources : wttj, francetravail, indeed, hellowork, dogfinance, meteojob, glassdoor, linkedin, apec")
    parser.add_argument("--dry-run", action="store_true", help="Simule le pipeline sans exécuter")
    parser.add_argument("--max", type=int, default=5, help="Max offres par source")
    parser.add_argument("--mode", choices=("full", "scan", "both"), default="full",
                        help="full = pipeline complet (CV/LM), scan = JobScanner uniquement, both = scan puis full")
    parser.add_argument("--scan-format", choices=("csv", "json"), default="csv",
                        help="Format sortie JobScanner (quand mode=scan ou both)")
    args = parser.parse_args()

    base_json = _load_base_json()
    sources = args.sources.split(",")

    if args.mode == "both":
        run_both(
            sources,
            base_json,
            max_jobs=args.max,
            dry_run=args.dry_run,
        )
    elif args.mode == "scan":
        from scheduler.job_scanner_runner import run as run_scan
        run_scan(
            sources,
            base_json,
            dry_run=args.dry_run,
            max_per_source=args.max,
            output_format=args.scan_format,
        )
    else:
        run(
            sources,
            base_json,
            dry_run=args.dry_run,
            max_per_source=args.max,
        )


if __name__ == "__main__":
    main()
