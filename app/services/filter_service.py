"""
Reel filter service module for IMM.
Provides criteria-based filtering for reels by keywords, hashtags, and usernames.
"""

from typing import List, Optional, Dict, Any
from app.models.reel import Reel
from app.utils.logger import logger


class ReelFilterService:
    """Service for filtering list of discovered reels based on user constraints."""

    def filter_by_keywords(
        self,
        reels: List[Reel],
        required_keywords: Optional[List[str]] = None,
        excluded_keywords: Optional[List[str]] = None
    ) -> List[Reel]:
        """Filters reels based on required and excluded keywords in their caption."""
        filtered: List[Reel] = []

        req_kw = [kw.lower().strip() for kw in (required_keywords or []) if kw.strip()]
        exc_kw = [kw.lower().strip() for kw in (excluded_keywords or []) if kw.strip()]

        for reel in reels:
            caption = (reel.caption or "").lower()

            # Check excluded keywords first
            if exc_kw and any(bad_word in caption for bad_word in exc_kw):
                logger.debug(f"Reel {reel.shortcode} skipped due to excluded keyword match.")
                continue

            # Check required keywords if specified
            if req_kw and not any(good_word in caption for good_word in req_kw):
                logger.debug(f"Reel {reel.shortcode} skipped due to missing required keywords.")
                continue

            filtered.append(reel)

        return filtered

    def filter_by_hashtags(self, reels: List[Reel], required_hashtags: List[str]) -> List[Reel]:
        """Filters reels to include only those containing at least one required hashtag."""
        if not required_hashtags:
            return reels

        target_tags = [
            f"#{tag.lstrip('#').lower().strip()}"
            for tag in required_hashtags
            if tag.strip()
        ]
        filtered: List[Reel] = []

        for reel in reels:
            caption = (reel.caption or "").lower()
            if any(tag in caption for tag in target_tags):
                filtered.append(reel)

        return filtered

    def filter_by_username(
        self,
        reels: List[Reel],
        allowed_usernames: Optional[List[str]] = None,
        blocked_usernames: Optional[List[str]] = None
    ) -> List[Reel]:
        """Filters reels based on allowed or blocked author usernames."""
        allowed = [u.lower().strip() for u in (allowed_usernames or []) if u.strip()]
        blocked = [u.lower().strip() for u in (blocked_usernames or []) if u.strip()]

        filtered: List[Reel] = []

        for reel in reels:
            author = reel.author_username.lower().strip()

            if blocked and author in blocked:
                logger.debug(f"Reel {reel.shortcode} skipped: author @{author} is blocked.")
                continue

            if allowed and author not in allowed:
                logger.debug(f"Reel {reel.shortcode} skipped: author @{author} is not in allowed list.")
                continue

            filtered.append(reel)

        return filtered

    def apply_filters(self, reels: List[Reel], criteria: Dict[str, Any]) -> List[Reel]:
        """
        Applies a series of filters sequentially according to the provided criteria dictionary.
        
        Example criteria dict:
        {
            "required_keywords": ["python", "tech"],
            "excluded_keywords": ["crypto", "scam"],
            "required_hashtags": ["automation"],
            "blocked_usernames": ["spam_account"]
        }
        """
        result = reels

        if "blocked_usernames" in criteria or "allowed_usernames" in criteria:
            result = self.filter_by_username(
                result,
                allowed_usernames=criteria.get("allowed_usernames"),
                blocked_usernames=criteria.get("blocked_usernames")
            )

        if "required_keywords" in criteria or "excluded_keywords" in criteria:
            result = self.filter_by_keywords(
                result,
                required_keywords=criteria.get("required_keywords"),
                excluded_keywords=criteria.get("excluded_keywords")
            )

        if "required_hashtags" in criteria:
            result = self.filter_by_hashtags(
                result,
                required_hashtags=criteria.get("required_hashtags")
            )

        logger.info(f"Filtering complete: {len(result)} of {len(reels)} reels passed filters.")
        return result
          
