"""
Deduplication service module for IMM.
Handles duplicate reel detection using SQLite database to prevent re-processing.
"""

from typing import List, Optional, Tuple
from app.database import fetch_one, execute_query
from app.models.reel import Reel
from app.utils.logger import logger


class DeduplicationService:
    """Service for checking and registering reels in the database to avoid duplicate handling."""

    def is_duplicate(self, reel_id: str) -> bool:
        """Checks whether a reel with the given reel_id already exists in database."""
        row = fetch_one("SELECT id FROM reels WHERE reel_id = ?", (reel_id,))
        return row is not None

    def filter_duplicates(self, reels: List[Reel]) -> Tuple[List[Reel], int]:
        """
        Filters out reels that already exist in the database.
        Returns a tuple of (unique_reels, duplicate_count).
        """
        unique_reels: List[Reel] = []
        duplicate_count = 0

        for reel in reels:
            if self.is_duplicate(reel.reel_id):
                duplicate_count += 1
                logger.debug(f"Duplicate reel skipped: {reel.reel_id} ({reel.shortcode})")
            else:
                unique_reels.append(reel)

        logger.info(
            f"Deduplication complete: {len(unique_reels)} new reels found, {duplicate_count} duplicates skipped."
        )
        return unique_reels, duplicate_count

    def register_reel(self, reel: Reel) -> Optional[int]:
        """Saves a new reel record into the SQLite database."""
        if self.is_duplicate(reel.reel_id):
            logger.warning(f"Attempted to register duplicate reel: {reel.reel_id}")
            return None

        query = """
            INSERT INTO reels (reel_id, shortcode, author_username, caption, url)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (
            reel.reel_id,
            reel.shortcode,
            reel.author_username,
            reel.caption,
            reel.url
        )
        inserted_id = execute_query(query, params)
        logger.info(f"Reel registered successfully in DB with internal ID: {inserted_id}")
        return inserted_id
          
