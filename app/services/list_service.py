"""
List management service module for IMM.
Handles blacklists and whitelists for usernames and terms in SQLite DB.
"""

from typing import List, Optional, Dict, Any
from app.database import execute_query, fetch_all, fetch_one
from app.utils.logger import logger


class ListService:
    """Service for managing blacklists and whitelists stored in list_entries table."""

    def add_entry(self, entry_value: str, list_type: str, reason: Optional[str] = None) -> bool:
        """
        Adds a new entry (username or keyword) to specified list ('blacklist' or 'whitelist').
        """
        list_type_clean = list_type.lower().strip()
        if list_type_clean not in ("blacklist", "whitelist"):
            logger.error(f"Invalid list_type: '{list_type}'. Must be 'blacklist' or 'whitelist'.")
            return False

        value_clean = entry_value.lower().strip()
        if not value_clean:
            return False

        query = """
            INSERT INTO list_entries (entry_value, list_type, reason)
            VALUES (?, ?, ?)
            ON CONFLICT(entry_value) DO UPDATE SET list_type=excluded.list_type, reason=excluded.reason;
        """
        try:
            execute_query(query, (value_clean, list_type_clean, reason))
            logger.info(f"Added '{value_clean}' to {list_type_clean}. Reason: {reason or 'None'}")
            return True
        except Exception as e:
            logger.error(f"Failed to add entry '{value_clean}' to {list_type_clean}: {e}")
            return False

    def add_to_blacklist(self, entry_value: str, reason: Optional[str] = None) -> bool:
        """Helper to add an entry to blacklist."""
        return self.add_entry(entry_value, "blacklist", reason)

    def add_to_whitelist(self, entry_value: str, reason: Optional[str] = None) -> bool:
        """Helper to add an entry to whitelist."""
        return self.add_entry(entry_value, "whitelist", reason)

    def is_blacklisted(self, entry_value: str) -> bool:
        """Checks if a username or keyword is in the blacklist."""
        value_clean = entry_value.lower().strip()
        row = fetch_one(
            "SELECT id FROM list_entries WHERE entry_value = ? AND list_type = 'blacklist'",
            (value_clean,)
        )
        return row is not None

    def is_whitelisted(self, entry_value: str) -> bool:
        """Checks if a username or keyword is in the whitelist."""
        value_clean = entry_value.lower().strip()
        row = fetch_one(
            "SELECT id FROM list_entries WHERE entry_value = ? AND list_type = 'whitelist'",
            (value_clean,)
        )
        return row is not None

    def get_entries(self, list_type: str) -> List[Dict[str, Any]]:
        """Retrieves all entries for a specific list type."""
        list_type_clean = list_type.lower().strip()
        rows = fetch_all(
            "SELECT entry_value, list_type, reason, created_at FROM list_entries WHERE list_type = ? ORDER BY id DESC",
            (list_type_clean,)
        )
        return [dict(row) for row in rows]

    def remove_entry(self, entry_value: str) -> bool:
        """Removes an entry from any list."""
        value_clean = entry_value.lower().strip()
        query = "DELETE FROM list_entries WHERE entry_value = ?"
        execute_query(query, (value_clean,))
        logger.info(f"Removed '{value_clean}' from list entries.")
        return True
      
