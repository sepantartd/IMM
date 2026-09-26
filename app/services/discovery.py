"""
Reel discovery service module for IMM.
Handles discovering reels from target usernames or search sources.
"""

from typing import List, Optional
from app.config import config
from app.instagram.client import InstagramClient
from app.models.reel import Reel
from app.utils.logger import logger


class ReelDiscoveryService:
    """Service for discovering and extracting reel metadata from target sources."""

    def __init__(self, client: Optional[InstagramClient] = None):
        self.client = client or InstagramClient()

    def discover_by_username(self, username: str, limit: int = 10) -> List[Reel]:
        """
        Discovers reels published by a specific username.
        Returns a list of Reel objects.
        """
        logger.info(f"Discovering reels for target username: @{username} (Limit: {limit})")
        reels: List[Reel] = []

        if config.DRY_RUN or not self.client.session_manager.is_session_available():
            logger.info(f"DRY_RUN or unauthenticated mode: generating simulated reels for @{username}.")
            for i in range(1, min(limit, 5) + 1):
                mock_shortcode = f"mock_{username}_{i}"
                reel = Reel(
                    reel_id=f"9900{i}{abs(hash(username)) % 10000}",
                    shortcode=mock_shortcode,
                    author_username=username,
                    url=f"https://www.instagram.com/reel/{mock_shortcode}/",
                    caption=f"Sample reel content #{i} from @{username} #python #automation"
                )
                reels.append(reel)
            return reels

        try:
            url = f"https://www.instagram.com/api/v1/feed/user/{username}/username/"
            response = self.client.client.get(url)
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                for item in items[:limit]:
                    if item.get("media_type") == 2 or item.get("product_type") == "clips":
                        pk = str(item.get("pk", ""))
                        code = item.get("code", "")
                        caption_text = ""
                        if item.get("caption") and isinstance(item["caption"], dict):
                            caption_text = item["caption"].get("text", "")

                        reel = Reel(
                            reel_id=pk,
                            shortcode=code,
                            author_username=username,
                            url=f"https://www.instagram.com/reel/{code}/",
                            caption=caption_text
                        )
                        reels.append(reel)
            else:
                logger.warning(f"Failed to fetch feed for @{username}, HTTP status: {response.status_code}")
        except Exception as e:
            logger.error(f"Error discovering reels for username @{username}: {e}")

        return reels

    def discover_by_keyword(self, keyword: str, limit: int = 10) -> List[Reel]:
        """
        Discovers reels matching a target keyword or topic.
        In DRY_RUN or simulated mode, returns mock structured items.
        """
        logger.info(f"Discovering reels for keyword: '{keyword}' (Limit: {limit})")
        reels: List[Reel] = []

        for i in range(1, min(limit, 3) + 1):
            mock_shortcode = f"kw_{keyword}_{i}"
            reel = Reel(
                reel_id=f"8800{i}{abs(hash(keyword)) % 10000}",
                shortcode=mock_shortcode,
                author_username=f"creator_{i}",
                url=f"https://www.instagram.com/reel/{mock_shortcode}/",
                caption=f"Exploring {keyword} in this amazing reel! #{keyword}"
            )
            reels.append(reel)

        return reels
        
