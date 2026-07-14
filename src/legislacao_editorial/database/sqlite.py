from __future__ import annotations

import sqlite3
from pathlib import Path

from ..models import LegalDocument


SCHEMA = """
CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    collected_at TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    article_count INTEGER NOT NULL,
    UNIQUE(source_url, content_hash)
);
"""


class SnapshotRepository:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as connection:
            connection.executescript(SCHEMA)

    def save(self, document: LegalDocument) -> bool:
        source = document.source
        with sqlite3.connect(self.path) as connection:
            cursor = connection.execute(
                """INSERT OR IGNORE INTO snapshots
                   (name, source_url, collected_at, content_hash, article_count)
                   VALUES (?, ?, ?, ?, ?)""",
                (source.name, source.url, source.collected_at.isoformat(), source.content_hash,
                 len(document.articles)),
            )
            return cursor.rowcount == 1

    def latest_hash(self, url: str) -> str | None:
        with sqlite3.connect(self.path) as connection:
            row = connection.execute(
                "SELECT content_hash FROM snapshots WHERE source_url = ? ORDER BY id DESC LIMIT 1",
                (url,),
            ).fetchone()
        return row[0] if row else None

