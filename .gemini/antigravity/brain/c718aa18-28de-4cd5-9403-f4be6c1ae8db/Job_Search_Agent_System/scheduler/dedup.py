"""
Déduplication : éviter de retraiter une offre déjà vue.
Stockage SQLite — additive, ne modifie pas le pipeline existant.
"""
import sqlite3
from datetime import datetime


class DedupStore:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS seen_jobs (
                url TEXT PRIMARY KEY,
                status TEXT DEFAULT 'processed',
                error TEXT,
                seen_at TEXT
            )
        """)
        self.conn.commit()

    def seen(self, url: str) -> bool:
        cur = self.conn.execute("SELECT 1 FROM seen_jobs WHERE url=?", (url,))
        return cur.fetchone() is not None

    def mark_seen(self, url: str) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO seen_jobs (url, status, seen_at) VALUES (?,?,?)",
            (url, "processed", datetime.now().isoformat()),
        )
        self.conn.commit()

    def mark_failed(self, url: str, error: str) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO seen_jobs (url, status, error, seen_at) VALUES (?,?,?,?)",
            (url, "failed", error, datetime.now().isoformat()),
        )
        self.conn.commit()
