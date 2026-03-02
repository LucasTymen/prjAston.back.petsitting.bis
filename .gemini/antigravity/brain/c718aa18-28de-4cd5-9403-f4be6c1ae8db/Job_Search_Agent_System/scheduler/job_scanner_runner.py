"""
JobScanner 24h — scan léger sans génération CV/LM.
Découverte (persona queries) → scrape → match → CSV uniquement.
Compatible JobSeeker / Job Scanner Mistral — sortie CSV.
Usage : python -m scheduler.job_scanner_runner --sources wttj --max 10
"""
import argparse
import json
import logging
from datetime import datetime
from pathlib import Path

from agents.scraper import ScraperOffre
from agents.matching import MatchingEngine
from scheduler.job_discoverer import discover_jobs
from scheduler.dedup import DedupStore
from storage.csv_exporter import (
    append_scan_line,
    build_scan_record,
    recommandation_jobscanner,
    write_scan_json,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STORAGE_DIR = PROJECT_ROOT / "storage"
LOGS_DIR = PROJECT_ROOT / "logs"
RESOURCES_DIR = PROJECT_ROOT / "resources"

LOGS_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "job_scanner.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("job_scanner")


def _load_base_json() -> dict:
    for name in ("cv_base_datas_pour_candidatures.json", "base.json"):
        path = RESOURCES_DIR / name
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    raise FileNotFoundError("Aucun profil trouvé dans resources/")


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
    out = {**base_json, "personas_specialises": personas}
    return out


def run(
    sources: list[str],
    base_json: dict,
    dry_run: bool = False,
    max_per_source: int = 10,
    output_path: Path | None = None,
    output_format: str = "csv",
) -> int:
    """
    Scan léger : discover → scrape → match → CSV ou JSON.
    Pas de CV/LM/email. Sortie JobScanner uniquement.
    """
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    dedup_path = STORAGE_DIR / "seen_jobs.db"
    dedup = DedupStore(str(dedup_path))

    ext = ".json" if output_format == "json" else ".csv"
    output_file = output_path or (STORAGE_DIR / "scans" / f"scan_{datetime.now().strftime('%Y%m%d_%H%M')}{ext}")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    base_with_personas = _ensure_personas(base_json)
    scraper = ScraperOffre()
    matching = MatchingEngine(base_with_personas)

    records: list[dict] = []
    total = 0
    for source in sources:
        source = source.strip().lower()
        log.info("Scan : %s", source)
        try:
            urls = discover_jobs(source, max_jobs=max_per_source, base_json=base_json)
            log.info("%s - %d offres", source, len(urls))
        except Exception as e:
            log.error("Erreur découverte %s : %s", source, e)
            continue

        for url in urls:
            if dedup.seen(url):
                log.debug("Skip (déjà vu) : %s", url[:60])
                continue

            log.info("Scan : %s", url[:80])
            try:
                if dry_run:
                    log.info("[DRY RUN] Skip scan pour %s", url[:60])
                    total += 1
                    continue

                # Scrape
                offre = scraper.process(url)
                # Match (sans génération CV/LM)
                match = matching.process(offre)

                recommandation = recommandation_jobscanner(match.score)
                top_kw = match.mots_cles_ats[:5] if match.mots_cles_ats else None
                rec = build_scan_record(
                    titre=offre.titre,
                    entreprise=offre.entreprise,
                    source=source,
                    localisation="",
                    secteur=match.secteur_detecte,
                    persona=match.persona_selectionne,
                    score_pct=match.score,
                    exposition_seniorite=match.exposition_seniorite,
                    recommandation=recommandation,
                    lien=url,
                    top_keywords=top_kw,
                )
                records.append(rec)
                if output_format == "csv":
                    append_scan_line(
                        path=output_file,
                        titre=offre.titre,
                        entreprise=offre.entreprise,
                        source=source,
                        localisation="",
                        secteur=match.secteur_detecte,
                        persona=match.persona_selectionne,
                        score_pct=match.score,
                        exposition_seniorite=match.exposition_seniorite,
                        recommandation=recommandation,
                        lien=url,
                        top_keywords=top_kw,
                    )

                log.info("OK — %s | %s | %d%% | %s", offre.titre[:40], match.persona_selectionne, match.score, recommandation)
                dedup.mark_seen(url)
                total += 1

            except Exception as e:
                log.error("Erreur scan %s : %s", url[:60], e)
                dedup.mark_failed(url, str(e))

    if output_format == "json":
        write_scan_json(output_file, records, sources=sources)
    log.info("Scan termine : %d offres -> %s", total, output_file)
    return total


def main() -> None:
    parser = argparse.ArgumentParser(description="JobScanner 24h — CSV ou JSON")
    parser.add_argument("--sources", default="wttj,francetravail,indeed,hellowork,dogfinance,meteojob,glassdoor,linkedin,apec,manpower,adecco",
                    help="wttj, francetravail, indeed, hellowork, dogfinance, meteojob, glassdoor, linkedin, apec, manpower, adecco")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max", type=int, default=10, help="Max offres par source")
    parser.add_argument("--format", choices=("csv", "json"), default="csv", help="Format de sortie")
    parser.add_argument("--output", "-o", help="Chemin fichier de sortie (extension selon --format)")
    args = parser.parse_args()

    base_json = _load_base_json()
    run(
        args.sources.split(","),
        base_json,
        dry_run=args.dry_run,
        max_per_source=args.max,
        output_path=Path(args.output) if args.output else None,
        output_format=args.format,
    )


if __name__ == "__main__":
    main()
