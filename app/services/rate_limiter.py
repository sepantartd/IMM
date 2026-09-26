"""
Rate limiter service module for IMM.
Tracks activity counts (hourly and daily) in SQLite to ensure limits are respected.
"""

from datetime import datetime, timedelta
from app.database import fetch_one, execute_query
from app.utils.logger import logger


class RateLimiterService:
    """Service to enforce hourly and daily action limits on automated tasks."""

    def __init__(self, max_per_hour: int = 10, max_per_day: int = 50):
        self.max_per_hour = max_per_hour
        self.max_per_day = max_per_day

    def record_action(self, action_type: str = "comment", details: str = "") -> None:
        """Logs an action in activity_logs table for rate limit tracking."""
        query = "INSERT INTO activity_logs (action_type, details) VALUES (?, ?)"
        execute_query(query, (action_type, details))
        logger.debug(f"Action '{action_type}' recorded in activity logs.")

    def get_action_count(self, action_type: str, hours: int) -> int:
        """Calculates total actions performed within the last N hours."""
        since_time = (datetime.now() - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
        query = """
            SELECT COUNT(*) as total 
            FROM activity_logs 
            WHERE action_type = ? AND timestamp >= ?
        """
        row = fetch_one(query, (action_type, since_time))
        return row["total"] if row else 0

    def can_proceed(self, action_type: str = "comment") -> bool:
        """
        Checks whether performing the specified action violates hourly or daily limits.
        Returns True if safe to proceed, False otherwise.
        """
        hourly_count = self.get_action_count(action_type, hours=1)
        if hourly_count >= self.max_per_hour:
            logger.warning(
                f"Hourly limit reached for '{action_type}': {hourly_count}/{self.max_per_hour}"
            )
            return False

        daily_count = self.get_action_count(action_type, hours=24)
        if daily_count >= self.max_per_day:
            logger.warning(
                f"Daily limit reached for '{action_type}': {daily_count}/{self.max_per_day}"
            )
            return False

        return True
      
