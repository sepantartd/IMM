import logging
from typing import List, Dict, Any
from app.instagram.client import InstagramClient
from app.instagram.errors import RateLimitException, UserNotFoundException, AuthException, InstagramError
from app.database import Database

logger = logging.getLogger(__name__)


class DiscoveryEngine:
    """Service responsible for discovering reels while respecting strict rate limits and deduplication."""

    def __init__(self, client: InstagramClient, db: Database):
        self.client = client
        self.db = db

    def discover_user_reels(self, username: str, limit: int = 10) -> Dict[str, Any]:
        """
        Discovers reels for a target username.
        Checks DB cooldown prior to execution and updates DB if 429 is encountered.
        """
        clean_username = username.lstrip("@").strip()
        result = {
            "username": clean_username,
            "discovered_count": 0,
            "new_count": 0,
            "rate_limited": False,
            "reels": [],
        }

        # 1. Check existing Cooldown status in Database
        if self.db.is_rate_limited("user_lookup") or self.db.is_rate_limited("reels_discovery"):
            logger.warning(
                f"[RATE-LIMIT] Discovery skipped for @{clean_username}: Rate limit cooldown is currently ACTIVE in DB."
            )
            result["rate_limited"] = True
            return result

        # 2. Lookup Target User ID
        try:
            logger.info(f"Discovering reels for target username: @{clean_username} (Limit: {limit})")
            user_id = self.client.get_user_id(clean_username)
        except RateLimitException as e:
            logger.error(f"[RATE-LIMIT] 429 hit during user lookup for @{clean_username}. Recording cooldown.")
            self.db.set_rate_limit(
                endpoint="user_lookup",
                retry_after_seconds=e.retry_after,
                error_type="RateLimitException",
                error_message=str(e),
            )
            result["rate_limited"] = True
            return result
        except UserNotFoundException:
            logger.warning(f"Target user @{clean_username} was not found on Instagram.")
            return result
        except (AuthException, InstagramError) as e:
            logger.error(f"Failed to resolve user ID for @{clean_username}: {e}")
            return result

        # 3. Retrieve User Reels
        try:
            reels = self.client.get_user_reels(user_id=user_id, limit=limit)
        except RateLimitException as e:
            logger.error(f"[RATE-LIMIT] 429 hit during reels retrieval for @{clean_username}. Recording cooldown.")
            self.db.set_rate_limit(
                endpoint="reels_discovery",
                retry_after_seconds=e.retry_after,
                error_type="RateLimitException",
                error_message=str(e),
            )
            result["rate_limited"] = True
            return result
        except (AuthException, InstagramError) as e:
            logger.error(f"Failed to fetch reels for user_id {user_id}: {e}")
            return result

        result["discovered_count"] = len(reels)

        # 4. Save and Deduplicate Reels in Database
        new_reels = []
        for reel in reels:
            inserted = self.db.insert_reel(
                media_id=reel["id"],
                shortcode=reel["code"],
                user_id=reel["user_id"],
                username=reel["username"],
                caption=reel["caption"],
            )
            if inserted:
                new_reels.append(reel)

        result["new_count"] = len(new_reels)
        result["reels"] = new_reels

        logger.info(
            f"Discovery run finished for @{clean_username}. "
            f"Discovered: {result['discovered_count']}, Unique New: {result['new_count']}"
        )
        return result
                
