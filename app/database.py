import sqlite3
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class Database:
    """SQLite Database Manager for IMM project supporting Rate Limits and Reels persistent storage."""

    def __init__(self, db_path: str = "data/imm.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Creates required tables if they do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Table for Rate Limits & Cooldowns
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rate_limits (
                    endpoint TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    detected_at TIMESTAMP NOT NULL,
                    cooldown_until TIMESTAMP NOT NULL,
                    retry_after_seconds INTEGER DEFAULT 3600,
                    error_type TEXT,
                    error_message TEXT
                )
            """)

            # Table for Discovered Reels
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reels (
                    media_id TEXT PRIMARY KEY,
                    shortcode TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    username TEXT NOT NULL,
                    caption TEXT,
                    discovered_at TIMESTAMP NOT NULL,
                    processed INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'pending'
                )
            """)

            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")

    # --- Rate Limit Operations ---

    def set_rate_limit(
        self,
        endpoint: str,
        retry_after_seconds: int = 3600,
        error_type: str = "RateLimitException",
        error_message: str = "HTTP 429 Too Many Requests",
    ) -> None:
        """Records a 429 Rate Limit event and calculates cooldown timestamp."""
        now = datetime.now(timezone.utc)
        cooldown_until = now + timedelta(seconds=retry_after_seconds)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO rate_limits (endpoint, status, detected_at, cooldown_until, retry_after_seconds, error_type, error_message)
                VALUES (?, 'cooldown', ?, ?, ?, ?, ?)
                ON CONFLICT(endpoint) DO UPDATE SET
                    status='cooldown',
                    detected_at=excluded.detected_at,
                    cooldown_until=excluded.cooldown_until,
                    retry_after_seconds=excluded.retry_after_seconds,
                    error_type=excluded.error_type,
                    error_message=excluded.error_message
                """,
                (
                    endpoint,
                    now.isoformat(),
                    cooldown_until.isoformat(),
                    retry_after_seconds,
                    error_type,
                    error_message[:255],
                ),
            )
            conn.commit()
            logger.warning(f"Rate limit set for endpoint '{endpoint}'. Cooldown until {cooldown_until.isoformat()}")

    def is_rate_limited(self, endpoint: str) -> bool:
        """Checks if a specific endpoint or global system is currently under cooldown."""
        now = datetime.now(timezone.utc)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT status, cooldown_until FROM rate_limits WHERE endpoint = ? OR endpoint = 'global'",
                (endpoint,),
            )
            rows = cursor.fetchall()

            for row in rows:
                if row["status"] == "cooldown":
                    cooldown_until = datetime.fromisoformat(row["cooldown_until"])
                    if now < cooldown_until:
                        return True
                    else:
                        self._clear_rate_limit(endpoint)
            return False

    def get_rate_limit_info(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Retrieves rate limit details for CLI or status checks."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM rate_limits WHERE endpoint = ?", (endpoint,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def _clear_rate_limit(self, endpoint: str) -> None:
        """Resets rate limit status when cooldown expires."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM rate_limits WHERE endpoint = ?", (endpoint,))
            conn.commit()
            logger.info(f"Cooldown period expired. Rate limit cleared for '{endpoint}'.")

    # --- Reels / Discovery Operations ---

    def insert_reel(self, media_id: str, shortcode: str, user_id: str, username: str, caption: str) -> bool:
        """Inserts a discovered reel into the database. Returns True if inserted, False if duplicate."""
        now = datetime.now(timezone.utc)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    INSERT INTO reels (media_id, shortcode, user_id, username, caption, discovered_at, processed, status)
                    VALUES (?, ?, ?, ?, ?, ?, 0, 'pending')
                    """,
                    (media_id, shortcode, user_id, username, caption, now.isoformat()),
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def get_pending_reels(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetches pending reels for processing."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM reels WHERE processed = 0 ORDER BY discovered_at ASC LIMIT ?",
                (limit,),
            )
            return [dict(row) for row in cursor.fetchall()]
                    
