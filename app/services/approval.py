"""
Approval service module for IMM.
Manages manual review, editing, approval, and rejection of generated comments.
"""

from typing import List, Optional
from app.database import execute_query, fetch_all
from app.models.comment import Comment
from app.utils.logger import logger


class ApprovalService:
    """Service for controlling human-in-the-loop manual approval flow for comments."""

    def save_pending_comment(self, comment: Comment) -> Optional[int]:
        """Saves a newly generated comment with status 'pending' into SQLite DB."""
        query = """
            INSERT INTO comments (reel_id, comment_text, status)
            VALUES (?, ?, 'pending')
        """
        comment_id = execute_query(query, (comment.reel_id, comment.comment_text))
        if comment_id:
            comment.id = comment_id
            logger.info(f"Saved pending comment ID {comment_id} for reel {comment.reel_id}")
        return comment_id

    def get_pending_comments(self) -> List[Comment]:
        """Retrieves all comments currently in 'pending' status."""
        rows = fetch_all("SELECT * FROM comments WHERE status = 'pending' ORDER BY id ASC")
        return [Comment.from_row(row) for row in rows]

    def get_approved_comments(self) -> List[Comment]:
        """Retrieves all comments ready for submission (status = 'approved')."""
        rows = fetch_all("SELECT * FROM comments WHERE status = 'approved' ORDER BY id ASC")
        return [Comment.from_row(row) for row in rows]

    def approve_comment(self, comment_id: int, updated_text: Optional[str] = None) -> bool:
        """Approves a pending comment, optionally updating its text before approval."""
        if updated_text:
            query = "UPDATE comments SET status = 'approved', comment_text = ? WHERE id = ?"
            params = (updated_text, comment_id)
        else:
            query = "UPDATE comments SET status = 'approved' WHERE id = ?"
            params = (comment_id,)

        execute_query(query, params)
        logger.info(f"Comment ID {comment_id} set to APPROVED.")
        return True

    def reject_comment(self, comment_id: int, reason: str = "Manual rejection") -> bool:
        """Rejects a pending comment."""
        query = "UPDATE comments SET status = 'rejected', error_message = ? WHERE id = ?"
        execute_query(query, (reason, comment_id))
        logger.info(f"Comment ID {comment_id} set to REJECTED. Reason: {reason}")
        return True
      
