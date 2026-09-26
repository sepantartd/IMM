"""
Comment submission service module for IMM.
Handles sending approved comments to Instagram endpoints or simulating posting in DRY_RUN mode.
"""

from datetime import datetime
from typing import Dict, Optional, List
from app.config import config
from app.database import execute_query
from app.instagram.client import InstagramClient
from app.models.comment import Comment
from app.services.approval import ApprovalService
from app.utils.logger import logger


class SubmissionService:
    """Service for submitting approved comments to Instagram reels and updating DB state."""

    def __init__(
        self,
        client: Optional[InstagramClient] = None,
        approval_service: Optional[ApprovalService] = None
    ):
        self.client = client or InstagramClient()
        self.approval_service = approval_service or ApprovalService()

    def submit_comment(self, comment: Comment) -> bool:
        """
        Submits a single approved comment.
        In DRY_RUN mode, simulates posting without network calls.
        Updates database status to 'submitted' or 'failed'.
        """
        if not comment.id:
            logger.error(f"Cannot submit comment without DB ID for reel {comment.reel_id}")
            return False

        logger.info(f"Attempting to submit comment ID {comment.id} for reel {comment.reel_id}...")

        # DRY_RUN Mode Simulation
        if config.DRY_RUN:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            query = """
                UPDATE comments 
                SET status = 'submitted', sent_at = ? 
                WHERE id = ?
            """
            execute_query(query, (now_str, comment.id))
            comment.status = "submitted"
            comment.sent_at = now_str
            logger.info(f"[DRY_RUN] Comment ID {comment.id} simulated as SUBMITTED successfully.")
            return True

        # Real Execution Mode
        try:
            url = f"https://www.instagram.com/api/v1/web/comments/{comment.reel_id}/add/"
            payload = {"comment_text": comment.comment_text}
            
            response = self.client.client.post(url, data=payload)

            if response.status_code == 200 and response.json().get("status") == "ok":
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                query = "UPDATE comments SET status = 'submitted', sent_at = ? WHERE id = ?"
                execute_query(query, (now_str, comment.id))
                comment.status = "submitted"
                comment.sent_at = now_str
                logger.info(f"Comment ID {comment.id} successfully posted to Instagram.")
                return True
            else:
                err_msg = f"HTTP {response.status_code}: {response.text[:100]}"
                query = "UPDATE comments SET status = 'failed', error_message = ? WHERE id = ?"
                execute_query(query, (err_msg, comment.id))
                comment.status = "failed"
                comment.error_message = err_msg
                logger.error(f"Failed to post comment ID {comment.id}: {err_msg}")
                return False

        except Exception as e:
            err_msg = str(e)
            query = "UPDATE comments SET status = 'failed', error_message = ? WHERE id = ?"
            execute_query(query, (err_msg, comment.id))
            comment.status = "failed"
            comment.error_message = err_msg
            logger.error(f"Error executing comment submission for ID {comment.id}: {err_msg}")
            return False

    def submit_approved_batch(self, limit: int = 5) -> Dict[str, int]:
        """
        Retrieves approved comments and submits them up to the specified limit.
        Returns a summary dictionary with successful and failed counts.
        """
        approved_comments = self.approval_service.get_approved_comments()
        targets = approved_comments[:limit]

        results = {"submitted": 0, "failed": 0, "total_processed": len(targets)}

        for comment in targets:
            success = self.submit_comment(comment)
            if success:
                results["submitted"] += 1
            else:
                results["failed"] += 1

        logger.info(f"Batch submission completed: {results}")
        return results
          
