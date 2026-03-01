"""
Persistance des candidatures — SQLite.
Additive : ne modifie pas le pipeline existant.
"""
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from core.models import FinalOutput


def _get_db_path() -> Path:
    """Base path pour les DB — storage/ à la racine du projet."""
    return Path(__file__).resolve().parent


def save_application(result: FinalOutput, job_url: str, db_path: str | None = None) -> None:
    """
    Enregistre une candidature en base SQLite.
    Schéma additif : n'interfère pas avec le pipeline.
    """
    base = Path(db_path) if db_path else _get_db_path()
    db_file = base / "applications.db"
    db_file.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_file))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_url TEXT UNIQUE NOT NULL,
            score INTEGER,
            status TEXT DEFAULT 'J0',
            result_json TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()

    score = result.matching.get("score") if isinstance(result.matching, dict) else None
    result_json = result.model_dump_json()

    conn.execute(
        """
        INSERT OR REPLACE INTO applications (job_url, score, status, result_json, created_at)
        VALUES (?, ?, 'J0', ?, ?)
        """,
        (job_url, score, result_json, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()
