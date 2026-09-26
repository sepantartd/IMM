"""
Instagram session management module for IMM.
Handles saving, loading, validating, and clearing user session data securely.
"""

import os
import json
from typing import Optional, Dict, Any
from app.utils.logger import logger

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
SESSION_FILE_PATH = os.path.join(DATA_DIR, "session.json")


class SessionManager:
    """Manages persistence and lifecycle of Instagram authentication sessions."""

    def __init__(self, session_path: str = SESSION_FILE_PATH):
        self.session_path = session_path

    def save_session(self, session_data: Dict[str, Any]) -> bool:
        """
        Saves session data (cookies, headers, tokens) to local session file.
        Returns True if successful, False otherwise.
        """
        try:
            os.makedirs(os.path.dirname(self.session_path), exist_ok=True)
            with open(self.session_path, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            logger.info("Session data saved successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to save session data: {e}")
            return False

    def load_session(self) -> Optional[Dict[str, Any]]:
        """
        Loads session data from local session file if available.
        Returns session dictionary or None.
        """
        if not os.path.exists(self.session_path):
            logger.debug("No existing session file found.")
            return None

        try:
            with open(self.session_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info("Session data loaded successfully.")
            return data
        except Exception as e:
            logger.error(f"Failed to load session file: {e}")
            return None

    def clear_session(self) -> bool:
        """Removes local session file."""
        if os.path.exists(self.session_path):
            try:
                os.remove(self.session_path)
                logger.info("Session cleared successfully.")
                return True
            except Exception as e:
                logger.error(f"Failed to delete session file: {e}")
                return False
        return True

    def is_session_available(self) -> bool:
        """Checks whether a valid non-empty session file exists."""
        data = self.load_session()
        if data and isinstance(data, dict) and len(data) > 0:
            return True
        return False
      
