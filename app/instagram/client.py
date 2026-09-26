"""
Instagram client module for IMM.
Handles HTTP communications, header construction, and authentication status verification.
"""

from typing import Dict, Any, Optional
import httpx
from app.config import config
from app.instagram.session import SessionManager
from app.utils.logger import logger


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
)


class InstagramClient:
    """HTTP Client wrapper for interacting with Instagram endpoints safely."""

    def __init__(self, session_manager: Optional[SessionManager] = None):
        self.session_manager = session_manager or SessionManager()
        self.headers = {
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept-Language": "en-US,en;q=0.9",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/",
        }
        self.client = httpx.Client(headers=self.headers, timeout=15.0, follow_redirects=True)
        self._apply_session()

    def _apply_session(self) -> None:
        """Applies stored session cookies to the httpx client if available."""
        session_data = self.session_manager.load_session()
        if session_data and "cookies" in session_data:
            for key, value in session_data["cookies"].items():
                self.client.cookies.set(key, value)
            logger.debug("Applied cookies from session storage to HTTP client.")

    def check_auth_status(self) -> Dict[str, Any]:
        """
        Verifies authentication status.
        In DRY_RUN or test mode without active credentials, returns safe simulated status.
        """
        if config.DRY_RUN and not self.session_manager.is_session_available():
            logger.info("DRY_RUN mode active and no session found. Returning dry-run status.")
            return {
                "authenticated": False,
                "status": "dry_run_unauthenticated",
                "message": "DRY_RUN mode enabled. No session stored.",
                "username": config.IG_USERNAME or "unknown"
            }

        session_data = self.session_manager.load_session()
        if not session_data or "cookies" not in session_data:
            return {
                "authenticated": False,
                "status": "no_session",
                "message": "No valid session or cookies available.",
                "username": config.IG_USERNAME or "unknown"
            }

        try:
            target_username = config.IG_USERNAME or "instagram"
            response = self.client.get(f"https://www.instagram.com/api/v1/users/web_profile_info/?username={target_username}")
            if response.status_code == 200:
                return {
                    "authenticated": True,
                    "status": "authenticated",
                    "message": "Session is active and valid.",
                    "username": config.IG_USERNAME
                }
            elif response.status_code in (401, 403):
                return {
                    "authenticated": False,
                    "status": "expired",
                    "message": "Session has expired or authentication is required.",
                    "username": config.IG_USERNAME
                }
            else:
                return {
                    "authenticated": False,
                    "status": "unknown",
                    "message": f"Response status: {response.status_code}",
                    "username": config.IG_USERNAME
                }
        except Exception as e:
            logger.error(f"Failed to verify authentication status: {e}")
            return {
                "authenticated": False,
                "status": "error",
                "message": f"Network error: {str(e)}",
                "username": config.IG_USERNAME
            }

    def close(self) -> None:
        """Closes underlying HTTP client resources."""
        self.client.close()
                  
