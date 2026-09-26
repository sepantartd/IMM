import logging
import os
from typing import Dict, Any
from app.instagram.client import InstagramClient
from app.instagram.errors import AuthException, RateLimitException
from app.database import Database
from app.services.discovery import DiscoveryEngine

logger = logging.getLogger(__name__)


class PipelineManager:
    """Service coordinating pipeline stage execution with rate limit safety checks."""

    def __init__(self, db_path: str = "data/imm.db", session_file: str = "data/session.json"):
        self.db = Database(db_path=db_path)
        self.client = InstagramClient(session_file=session_file)

    def run_discovery(self, target_username: str, limit: int = 10) -> Dict[str, Any]:
        """Runs the Discovery stage safely with session verification and error handling."""
        session_id = os.getenv("INSTAGRAM_SESSION_ID")

        logger.info("Initializing Instagram Session for Discovery Pipeline...")
        try:
            self.client.initialize_session(session_id=session_id)
        except AuthException as e:
            logger.error(f"Pipeline execution stopped: Authentication failed - {e}")
            return {"status": "failed", "reason": "auth_error", "message": str(e)}
        except RateLimitException as e:
            logger.error(f"Pipeline execution stopped: Session rate limited - {e}")
            self.db.set_rate_limit(
                endpoint="session_init",
                retry_after_seconds=e.retry_after,
                error_type="RateLimitException",
                error_message=str(e),
            )
            return {"status": "rate_limited", "reason": "session_rate_limit", "message": str(e)}

        engine = DiscoveryEngine(client=self.client, db=self.db)
        discovery_result = engine.discover_user_reels(username=target_username, limit=limit)

        if discovery_result["rate_limited"]:
            return {
                "status": "rate_limited",
                "discovered_reels": 0,
                "new_reels": 0,
                "details": discovery_result,
            }

        return {
            "status": "success",
            "discovered_reels": discovery_result["discovered_count"],
            "new_reels": discovery_result["new_count"],
            "details": discovery_result,
        }
        
