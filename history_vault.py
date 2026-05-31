"""
history_vault.py — Persistent local history logging for LocalFlow.

Uses SQLite to store every dictation result with timestamps.
The database file is co-located with the application files.
"""

import sqlite3
import os
from datetime import datetime


# ---------------------------------------------------------------------------
# Database path — same directory as this script
# ---------------------------------------------------------------------------
DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "localflow_history.db",
)


class HistoryVault:
    """Persistent SQLite-backed dictation history log."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------
    def _init_db(self) -> None:
        """Create the history table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp     TEXT    NOT NULL,
                    raw_text      TEXT    DEFAULT '',
                    polished_text TEXT    NOT NULL,
                    created_at    REAL    NOT NULL
                )
            """)
            conn.commit()

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------
    def add_entry(self, polished_text: str, raw_text: str = "") -> str:
        """
        Log a dictation result.

        Args:
            polished_text: The final LLM-polished text.
            raw_text:      The raw Whisper transcription (optional).

        Returns:
            The formatted timestamp string for display.
        """
        timestamp = datetime.now().strftime("%b %d, %Y — %I:%M %p")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO history (timestamp, raw_text, polished_text, created_at) "
                "VALUES (?, ?, ?, ?)",
                (timestamp, raw_text, polished_text, datetime.now().timestamp()),
            )
            conn.commit()
        return timestamp

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def get_recent(self, limit: int = 50) -> list[tuple[str, str]]:
        """
        Fetch recent history entries in reverse chronological order.

        Returns:
            List of (timestamp, polished_text) tuples.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT timestamp, polished_text FROM history "
                "ORDER BY id DESC LIMIT ?",
                (limit,),
            )
            return cursor.fetchall()

    def count(self) -> int:
        """Return the total number of history entries."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM history")
            return cursor.fetchone()[0]

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------
    def clear(self) -> None:
        """Wipe all history entries."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM history")
            conn.commit()
