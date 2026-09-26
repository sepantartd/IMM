"""
Automation Pipeline Orchestrator module for IMM.
Coordinates discovery, filtering, deduplication, comment generation, approval, and submission.
"""

from typing import Dict, Any, List, Optional
from app.config import config
from app.instagram.client import InstagramClient
from app.services.discovery import ReelDiscoveryService
from app.services.filter_service import ReelFilterService
from app.services.deduplication import DeduplicationService
from app.services.comment_generator import CommentGeneratorService
from app.services.approval import ApprovalService
from app.services.submission_service import SubmissionService
from app.services.rate_limiter import RateLimiterService
from app.services.list_service import ListService
from app.utils.delays import random_delay
from app.utils.logger import logger


class AutomationPipeline:
    """Orchestrates end-to-end automation operations for IMM."""

    def __init__(self):
        self.client = InstagramClient()
        self.discovery_svc = ReelDiscoveryService(client=self.client)
        self.filter_svc = ReelFilterService()
        self.dedup_svc = DeduplicationService()
        self.comment_gen_svc = CommentGeneratorService()
        self.approval_svc = ApprovalService()
        self.submission_svc = SubmissionService(client=self.client, approval_service=self.approval_svc)
        self.rate_limiter_svc = RateLimiterService()
        self.list_svc = ListService()

    def run_discovery_and_generation(
        self,
        target: str,
        mode: str = "username",
        limit: int = 10,
        criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Runs the discovery to generation pipeline:
        Discovery -> Filter (DB Blacklist + Custom) -> Deduplication -> Comment Generation -> Pending Queue
        """
        logger.info(f"Starting pipeline stage: Discovery and Generation for target '{target}' ({mode}).")
        stats = {
            "discovered": 0,
            "passed_filters": 0,
            "unique": 0,
            "comments_generated": 0
        }

        # 1. Discovery
        if mode == "username":
            raw_reels = self.discovery_svc.discover_by_username(target, limit=limit)
        else:
            raw_reels = self.discovery_svc.discover_by_keyword(target, limit=limit)

        stats["discovered"] = len(raw_reels)
        if not raw_reels:
            logger.info("No reels discovered. Pipeline run finished.")
            return stats

        # 2. Filter (Merge DB Blacklist)
        filter_criteria = criteria or {}
        db_blacklists = [e["entry_value"] for e in self.list_svc.get_entries("blacklist")]
        existing_blocked = filter_criteria.get("blocked_usernames", [])
        filter_criteria["blocked_usernames"] = list(set(existing_blocked + db_blacklists))

        filtered_reels = self.filter_svc.apply_filters(raw_reels, filter_criteria)
        stats["passed_filters"] = len(filtered_reels)

        # 3. Deduplication
        unique_reels, _ = self.dedup_svc.filter_duplicates(filtered_reels)
        stats["unique"] = len(unique_reels)

        # 4. Save Reels & Generate Comments into Pending Queue
        for reel in unique_reels:
            self.dedup_svc.register_reel(reel)
            comment = self.comment_gen_svc.generate_comment(reel)
            self.approval_svc.save_pending_comment(comment)
            stats["comments_generated"] += 1

        logger.info(f"Discovery and generation completed successfully: {stats}")
        return stats

    def process_approved_submissions(self, batch_limit: int = 5) -> Dict[str, int]:
        """
        Processes approved comments queue with rate limiting and safety delays:
        Queue Fetch -> Rate Check -> Delay -> Post -> Log Action
        """
        logger.info("Starting pipeline stage: Processing Approved Submissions.")
        approved_comments = self.approval_svc.get_approved_comments()
        targets = approved_comments[:batch_limit]

        results = {"submitted": 0, "failed": 0, "skipped_rate_limit": 0}

        for comment in targets:
            # Check rate limits before each action
            if not self.rate_limiter_svc.can_proceed("comment"):
                logger.warning("Action limit reached during submission loop. Halting processing.")
                results["skipped_rate_limit"] += (len(targets) - (results["submitted"] + results["failed"]))
                break

            # Apply human-like delay
            random_delay(2.0, 5.0)

            # Submit comment
            success = self.submission_svc.submit_comment(comment)
            if success:
                results["submitted"] += 1
                self.rate_limiter_svc.record_action("comment", details=f"Reel ID: {comment.reel_id}")
            else:
                results["failed"] += 1

        logger.info(f"Submissions processing finished: {results}")
        return results

    def close(self) -> None:
        """Closes internal HTTP client resources."""
        self.client.close()
  
