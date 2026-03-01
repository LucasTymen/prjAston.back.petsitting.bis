"""
Cron dédié aux relances J+4 et J+10.
Lance séparément du cron principal.
Usage : python -m scheduler.followup_runner [--dry-run]
"""
import argparse
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STORAGE_DIR = PROJECT_ROOT / "storage"
LOGS_DIR = PROJECT_ROOT / "logs"

LOGS_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "followup.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("followup_runner")


def _get_db_path() -> Path:
    return STORAGE_DIR / "applications.db"


def run_followups(db_path: Path | None = None, dry_run: bool = False) -> int:
    """
    Relances J+4 et J+10 à partir des candidatures en base.
    - J+4 : status='J0' et (today - created_at).days == 4
    - J+10 : status='relance_j4' et (today - created_at).days == 10
    """
    db_file = db_path or _get_db_path()
    if not db_file.exists():
        log.warning("Base applications introuvable : %s", db_file)
        return 0

    conn = sqlite3.connect(str(db_file))
    conn.row_factory = sqlite3.Row
    today = datetime.now().date()
    sent = 0

    rows = conn.execute("""
        SELECT id, job_url, status, result_json, created_at
        FROM applications
        WHERE status IN ('J0', 'envoyee', 'relance_j4')
        AND result_json IS NOT NULL
    """).fetchall()

    for row in rows:
        id_ = row["id"]
        job_url = row["job_url"]
        status = row["status"]
        result_json_str = row["result_json"]
        created_at_str = row["created_at"]

        try:
            s = (created_at_str or "")[:19].replace("Z", "+00:00")
            date_cand = datetime.fromisoformat(s).date()
        except (ValueError, TypeError):
            date_cand = datetime.fromisoformat((created_at_str or "")[:10]).date() if (created_at_str and len(created_at_str) >= 10) else None
        if not date_cand:
            continue

        try:
            data = json.loads(result_json_str)
        except (json.JSONDecodeError, TypeError):
            log.warning("JSON invalide id=%s", id_)
            continue

        offre = data.get("offre", {})
        canal = data.get("canal_application", {})
        emails = data.get("emails") or {}
        email_contact = canal.get("contact_cible") or data.get("email_trouve", {}).get("email_trouve") or ""
        if not email_contact or email_contact == "Inconnu":
            log.debug("Pas d'email pour id=%s %s", id_, offre.get("entreprise", "?"))
            continue

        entreprise = offre.get("entreprise", "?")
        titre = offre.get("titre", "?")
        mail_j4 = (emails.get("email_j4") or "").strip()
        mail_j10 = (emails.get("email_j10") or "").strip()
        sujet = (emails.get("sujet") or f"Relance candidature — {titre}").strip()

        delta = (today - date_cand).days

        if delta == 4 and status in ("J0", "envoyee") and mail_j4:
            log.info("Relance J+4 -> %s (%s)", entreprise, email_contact)
            if not dry_run:
                _send_followup(email_contact, sujet, mail_j4, "j4")
                conn.execute("UPDATE applications SET status='relance_j4' WHERE id=?", (id_,))
                conn.commit()
                sent += 1

        elif delta >= 10 and status == "relance_j4" and mail_j10:
            log.info("Relance J+10 -> %s (%s)", entreprise, email_contact)
            if not dry_run:
                _send_followup(email_contact, sujet, mail_j10, "j10")
                conn.execute("UPDATE applications SET status='relance_j10' WHERE id=?", (id_,))
                conn.commit()
                sent += 1

    conn.close()
    log.info("Relances terminées — %d envoyées", sent)
    return sent


def _send_followup(to_email: str, subject: str, body: str, type_: str) -> None:
    """
    Crée un brouillon Gmail via GmailDraftingAgent.
    """
    from agents.drafting import GmailDraftingAgent

    agent = GmailDraftingAgent()
    prefix = "J+4" if type_ == "j4" else "J+10"
    full_subject = f"Re: {subject}" if not subject.startswith("Re:") else subject
    agent.create_draft(to_email=to_email, subject=full_subject, body=body, attachment_paths=[])
    log.info("Brouillon %s créé pour %s", prefix, to_email)


def main() -> None:
    parser = argparse.ArgumentParser(description="Relances J+4 / J+10")
    parser.add_argument("--dry-run", action="store_true", help="Simule sans envoyer")
    parser.add_argument("--db", help="Chemin vers applications.db")
    args = parser.parse_args()

    db_path = Path(args.db) if args.db else None
    run_followups(db_path=db_path, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
