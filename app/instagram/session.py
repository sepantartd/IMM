import json
import logging
from pathlib import Path
from typing import Optional
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, PleaseWait429, RateLimitError

from app.instagram.errors import AuthException, RateLimitException

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages Instagrapi session persistence using JSON settings."""

    def __init__(self, session_file_path: str = "data/session.json"):
        self.session_file = Path(session_file_path)
        self.session_file.parent.mkdir(parents=True, exist_ok=True)

    def load_session(self, client: Client, fallback_session_id: Optional[str] = None) -> bool:
        """
        Loads session into instagrapi Client.
        Prioritizes session.json file, falls back to raw sessionid string if provided.
        """
        if self.session_file.exists():
            try:
                logger.info(f"Loading session settings from {self.session_file}")
                client.load_settings(self.session_file)
                return True
            except Exception as e:
                logger.warning(f"Failed to load session settings file: {e}")

        if fallback_session_id and fallback_session_id.strip():
            logger.info("Initializing session from INSTAGRAM_SESSION_ID environment variable.")
            try:
                client.set_settings({})
                client.login_by_sessionid(fallback_session_id.strip())
                self.save_session(client)
                return True
            except (PleaseWait429, RateLimitError) as e:
                raise RateLimitException("Rate limit encountered during session creation.") from e
            except Exception as e:
                raise AuthException(f"Failed to authenticate using sessionid: {e}") from e

        logger.warning("No valid session settings or session ID available.")
        return False

    def save_session(self, client: Client) -> None:
        """Saves current instagrapi client settings to JSON file."""
        try:
            self.session_file.parent.mkdir(parents=True, exist_ok=True)
            client.dump_settings(self.session_file)
            logger.info(f"Session settings successfully saved to {self.session_file}")
        except Exception as e:
            logger.error(f"Failed to save session settings: {e}")
            
