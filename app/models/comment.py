"""
Comment data model for IMM.
Represents a comment entity and its lifecycle status.
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import sqlite3


@dataclass
class Comment:
    """Represents a comment generated or submitted for a specific reel."""
    
    reel_id: str
    comment_text: str
    status: str = "pending"  # Allowed: 'pending', 'approved', 'submitted', 'failed', 'rejected'
    sent_at: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converts the Comment object into a dictionary."""
        return asdict(self)

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Comment":
        """Constructs a Comment object from a database Row."""
        return cls(
            id=row["id"],
            reel_id=row["reel_id"],
            comment_text=row["comment_text"],
            status=row["status"],
            sent_at=row["sent_at"],
            error_message=row["error_message"],
            created_at=row["created_at"]
        )
      
