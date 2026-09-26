"""
Analytics and reporting service module for IMM.
Calculates key performance metrics, success rates, and generates summary reports.
"""

import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
from app.database import fetch_one, fetch_all
from app.utils.logger import logger


class AnalyticsService:
    """Service for computing system activity analytics and generating reports."""

    def get_summary_stats(self) -> Dict[str, Any]:
        """Calculates total counts and performance metrics across the entire system."""
        total_reels = fetch_one("SELECT COUNT(*) as count FROM reels")["count"]

        comments_by_status = fetch_all(
            "SELECT status, COUNT(*) as count FROM comments GROUP BY status"
        )
        status_map = {row["status"]: row["count"] for row in comments_by_status}

        pending = status_map.get("pending", 0)
        approved = status_map.get("approved", 0)
        submitted = status_map.get("submitted", 0)
        rejected = status_map.get("rejected", 0)
        failed = status_map.get("failed", 0)
        total_comments = sum(status_map.values())

        submitted_attempts = submitted + failed
        success_rate = (submitted / submitted_attempts * 100.0) if submitted_attempts > 0 else 0.0

        return {
            "total_reels": total_reels,
            "total_comments": total_comments,
            "pending_comments": pending,
            "approved_comments": approved,
            "submitted_comments": submitted,
            "rejected_comments": rejected,
            "failed_comments": failed,
            "success_rate_pct": round(success_rate, 2)
        }

    def get_daily_activity(self, days: int = 7) -> List[Dict[str, Any]]:
        """Retrieves daily comment activity breakdown for the last N days."""
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        query = """
            SELECT DATE(created_at) as date, status, COUNT(*) as count
            FROM comments
            WHERE DATE(created_at) >= ?
            GROUP BY DATE(created_at), status
            ORDER BY date ASC
        """
        rows = fetch_all(query, (since_date,))

        daily_map: Dict[str, Dict[str, Any]] = {}
        for row in rows:
            d = row["date"]
            if d not in daily_map:
                daily_map[d] = {
                    "date": d,
                    "submitted": 0,
                    "failed": 0,
                    "pending": 0,
                    "approved": 0,
                    "rejected": 0
                }
            st = row["status"]
            if st in daily_map[d]:
                daily_map[d][st] = row["count"]

        return list(daily_map.values())

    def export_report_json(self, filepath: str) -> bool:
        """Exports full summary analytics and recent activity to a JSON file."""
        try:
            data = {
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "summary": self.get_summary_stats(),
                "daily_activity_7d": self.get_daily_activity(7)
            }
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Analytics report successfully exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export JSON report: {e}")
            return False
      
