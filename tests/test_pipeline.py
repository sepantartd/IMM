"""
Integration test suite for IMM core pipeline and services.
Run via: python -m unittest discover tests OR pytest
"""

import os
import unittest
from app.config import config
from app.database import init_db, fetch_one, execute_query
from app.models.reel import Reel
from app.models.comment import Comment
from app.services import (
    ReelFilterService,
    DeduplicationService,
    CommentGeneratorService,
    ApprovalService,
    RateLimiterService,
    ListService,
    AutomationPipeline
)


class TestIMMPipeline(unittest.TestCase):
    """Test cases covering IMM core services and workflow."""

    @classmethod
    def setUpClass(cls):
        """Ensure DRY_RUN is enabled and database is initialized for tests."""
        config.DRY_RUN = True
        init_db()

    def test_01_database_initialization(self):
        """Verify database tables creation."""
        row = fetch_one("SELECT name FROM sqlite_master WHERE type='table' AND name='reels';")
        self.assertIsNotNone(row, "Table 'reels' should exist in SQLite database.")

    def test_02_filter_service(self):
        """Test reel filtering by required/excluded keywords and blocked users."""
        filter_svc = ReelFilterService()
        reels = [
            Reel(reel_id="t1", shortcode="s1", author_username="user1", url="http://..", caption="Python coding tutorial #python"),
            Reel(reel_id="t2", shortcode="s2", author_username="spammer", url="http://..", caption="Crypto giveaway #crypto"),
        ]

        criteria = {
            "required_keywords": ["python"],
            "excluded_keywords": ["crypto"],
            "blocked_usernames": ["spammer"]
        }
        filtered = filter_svc.apply_filters(reels, criteria)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].reel_id, "t1")

    def test_03_deduplication_service(self):
        """Test deduplication and registering new reels."""
        dedup_svc = DeduplicationService()
        test_reel = Reel(reel_id="test_dedup_001", shortcode="sc001", author_username="dev", url="http://..", caption="Test")

        # First registration
        registered_id = dedup_svc.register_reel(test_reel)
        self.assertIsNotNone(registered_id)

        # Checking duplicate
        self.assertTrue(dedup_svc.is_duplicate("test_dedup_001"))

    def test_04_comment_generation_and_approval(self):
        """Test comment generation and manual approval flow."""
        comment_gen = CommentGeneratorService()
        approval_svc = ApprovalService()

        test_reel = Reel(reel_id="test_gen_002", shortcode="sc002", author_username="alex", url="http://..", caption="AI news")
        comment = comment_gen.generate_comment(test_reel, custom_template="Nice post @{username}!")

        self.assertIn("alex", comment.comment_text)

        db_id = approval_svc.save_pending_comment(comment)
        self.assertIsNotNone(db_id)

        # Approve comment
        approval_svc.approve_comment(db_id)
        approved_items = approval_svc.get_approved_comments()
        
        approved_ids = [c.id for c in approved_items]
        self.assertIn(db_id, approved_ids)

    def test_05_rate_limiter(self):
        """Test rate limiter threshold checking."""
        limiter = RateLimiterService(max_per_hour=2, max_per_day=5)
        limiter.record_action("test_action", "details 1")
        limiter.record_action("test_action", "details 2")

        self.assertFalse(limiter.can_proceed("test_action"))

    def test_06_list_service(self):
        """Test blacklisting and whitelisting functionality."""
        list_svc = ListService()
        list_svc.add_to_blacklist("bad_actor_99", reason="Test spammer")

        self.assertTrue(list_svc.is_blacklisted("bad_actor_99"))
        self.assertFalse(list_svc.is_blacklisted("good_actor_01"))

    def test_07_full_pipeline_run(self):
        """Test full end-to-end execution flow via AutomationPipeline."""
        pipeline = AutomationPipeline()
        try:
            stats = pipeline.run_discovery_and_generation(
                target="coder_daily",
                mode="username",
                limit=2
            )
            self.assertGreaterEqual(stats["discovered"], 1)

            sub_results = pipeline.process_approved_submissions(batch_limit=2)
            self.assertIn("submitted", sub_results)
        finally:
            pipeline.close()


if __name__ == "__main__":
    unittest.main()
      
