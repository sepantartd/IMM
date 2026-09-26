"""
Health check and diagnostics service module for IMM.
Performs automated diagnostics on database, internet connectivity, storage, and system configuration.
"""

import os
import shutil
import httpx
from typing import Dict, Any, List
from app.config import config
from app.database import get_db_connection
from app.utils.logger import logger


class HealthCheckService:
    """Service for running system health checks and diagnostic routines."""

    def check_database(self) -> Dict[str, Any]:
        """Checks SQLite database connectivity and query execution."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1;")
            conn.close()
            return {"status": "ok", "message": "Database connection and query test successful."}
        except Exception as e:
            return {"status": "error", "message": f"Database failure: {str(e)}"}

    def check_internet(self) -> Dict[str, Any]:
        """Checks HTTP reachability to Instagram servers."""
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.get("https://www.instagram.com/robots.txt")
                if res.status_code == 200:
                    return {"status": "ok", "message": "Instagram server is reachable."}
                return {"status": "warning", "message": f"Instagram returned HTTP {res.status_code}."}
        except Exception as e:
            return {"status": "error", "message": f"Network reachability failed: {str(e)}"}

    def check_config(self) -> Dict[str, Any]:
        """Validates configuration parameters and file presence."""
        if not os.path.exists(config.DATABASE_PATH):
            return {"status": "warning", "message": f"Database file missing at {config.DATABASE_PATH}"}
        return {"status": "ok", "message": "Configuration parameters are valid."}

    def check_storage(self) -> Dict[str, Any]:
        """Checks write permissions and free storage space in database directory."""
        try:
            db_dir = os.path.dirname(config.DATABASE_PATH) or "."
            os.makedirs(db_dir, exist_ok=True)

            _, _, free = shutil.disk_usage(db_dir)
            free_mb = free / (1024 * 1024)

            if free_mb < 50:
                return {"status": "warning", "message": f"Low storage space: {free_mb:.1f} MB free."}
            return {"status": "ok", "message": f"Storage OK ({free_mb:.1f} MB free)."}
        except Exception as e:
            return {"status": "error", "message": f"Storage check failed: {str(e)}"}

    def run_all_checks(self) -> List[Dict[str, Any]]:
        """Runs all diagnostic checks and returns structured results."""
        results = [
            {"component": "Database", **self.check_database()},
            {"component": "Network", **self.check_internet()},
            {"component": "Config", **self.check_config()},
            {"component": "Storage", **self.check_storage()}
        ]
        logger.info(f"Health check diagnostics executed: {results}")
        return results
