"""
Database backup and maintenance service module for IMM.
Provides automated SQLite backups, database vacuuming, and log purging functions.
"""

import os
import shutil
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.config import config
from app.database import get_db_connection, execute_query
from app.utils.logger import logger


class DatabaseBackupService:
    """Service for handling SQLite database backups and periodic maintenance routines."""

    def create_backup(self, backup_dir: str = "data/backups") -> Optional[str]:
        """Creates a timestamped copy of the SQLite database file."""
        if not os.path.exists(config.DATABASE_PATH):
            logger.error(f"Cannot backup: Database file not found at {config.DATABASE_PATH}")
            return None

        try:
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"imm_backup_{timestamp}.db"
            backup_path = os.path.join(backup_dir, backup_filename)

            shutil.copy2(config.DATABASE_PATH, backup_path)
            logger.info(f"Database backup successfully created at: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create database backup: {e}")
            return None

    def vacuum_database(self) -> bool:
        """Executes VACUUM command to defragment and optimize SQLite file size."""
        try:
            conn = get_db_connection()
            conn.execute("VACUUM;")
            conn.close()
            logger.info("Database VACUUM optimization completed successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to execute VACUUM on database: {e}")
            return False

    def purge_old_logs(self, days: int = 30) -> int:
        """Purges records in activity_logs older than specified number of days."""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
            query = "DELETE FROM activity_logs WHERE timestamp < ?"
            deleted_count = execute_query(query, (cutoff_date,))
            logger.info(f"Purged old activity logs prior to {cutoff_date}. Total rows removed: {deleted_count}")
            return deleted_count or 0
        except Exception as e:
            logger.error(f"Failed to purge old logs: {e}")
            return 0

    def run_full_maintenance(self, backup_first: bool = True, purge_days: int = 30) -> Dict[str, Any]:
        """Runs complete maintenance cycle: Backup -> Purge Logs -> Vacuum."""
        results = {
            "backup_path": None,
            "purged_logs": 0,
            "vacuum_success": False
        }

        if backup_first:
            results["backup_path"] = self.create_backup()

        results["purged_logs"] = self.purge_old_logs(days=purge_days)
        results["vacuum_success"] = self.vacuum_database()

        return results
          
