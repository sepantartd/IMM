import logging
from typing import List, Dict, Any, Optional
from instagrapi import Client
from instagrapi.exceptions import (
    PleaseWait429,
    RateLimitError,
    LoginRequired,
    UserNotFound,
    ClientError,
    ClientConnectionError,
)

from app.instagram.session import SessionManager
from app.instagram.errors import (
    InstagramError,
    RateLimitException,
    AuthException,
    NetworkException,
    UserNotFoundException,
)

logger = logging.getLogger(__name__)


class InstagramClient:
    """
    Adapter class wrapping instagrapi.Client.
    Translates instagrapi exceptions into domain-specific exceptions.
    """

    def __init__(self, session_file: str = "data/session.json"):
        self._client = Client()
        self._session_manager = SessionManager(session_file_path=session_file)
        self._is_authenticated = False

    def initialize_session(self, session_id: Optional[str] = None) -> bool:
        """Loads and verifies the session without making aggressive API calls."""
        try:
            success = self._session_manager.load_session(self._client, fallback_session_id=session_id)
            if success:
                self._is_authenticated = True
            return success
        except (RateLimitException, AuthException):
            raise
        except Exception as e:
            raise AuthException(f"Session initialization failed: {e}") from e

    def get_user_id(self, username: str) -> str:
        """Retrieves user ID for a given username using Mobile API."""
        clean_username = username.lstrip("@").strip()
        try:
            user_id = self._client.user_id_from_username(clean_username)
            return str(user_id)
        except (PleaseWait429, RateLimitError) as e:
            logger.error(f"Rate limit hit while retrieving user ID for @{clean_username}")
            raise RateLimitException("Instagram returned HTTP 429 during user lookup.") from e
        except UserNotFound as e:
            logger.warning(f"User @{clean_username} not found on Instagram.")
            raise UserNotFoundException(f"User @{clean_username} does not exist.") from e
        except LoginRequired as e:
            logger.error("Session expired or login required.")
            raise AuthException("Instagram session is invalid or expired.") from e
        except ClientConnectionError as e:
            logger.error(f"Network connection error: {e}")
            raise NetworkException("Failed to connect to Instagram servers.") from e
        except ClientError as e:
            if "429" in str(e):
                raise RateLimitException("Rate limit hit (HTTP 429).") from e
            raise InstagramError(f"Instagram client error: {e}") from e

    def get_user_reels(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves latest Clips/Reels for a given user ID."""
        try:
            clips = self._client.user_clips(int(user_id), amount=limit)
            reels_data = []
            for clip in clips:
                reels_data.append({
                    "id": str(clip.pk),
                    "code": clip.code,
                    "caption": clip.caption_text if clip.caption_text else "",
                    "taken_at": clip.taken_at,
                    "user_id": str(user_id),
                    "username": clip.user.username if clip.user else "",
                    "view_count": getattr(clip, "view_count", 0),
                    "like_count": getattr(clip, "like_count", 0),
                    "comment_count": getattr(clip, "comment_count", 0),
                })
            return reels_data
        except (PleaseWait429, RateLimitError) as e:
            logger.error(f"Rate limit hit while fetching reels for user_id {user_id}")
            raise RateLimitException("Instagram returned HTTP 429 during reels retrieval.") from e
        except LoginRequired as e:
            raise AuthException("Session expired while fetching reels.") from e
        except ClientConnectionError as e:
            raise NetworkException("Network failure during reels fetch.") from e
        except ClientError as e:
            if "429" in str(e):
                raise RateLimitException("Rate limit hit (HTTP 429).") from e
            raise InstagramError(f"Error fetching reels: {e}") from e
            
