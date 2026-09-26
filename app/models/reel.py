"""
Reel data model for IMM.
Represents an Instagram reel entity and provides serialization helpers.
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import sqlite3


@dataclass
class Reel:
    """Represents an Instagram Reel item."""
    
    reel_id: str
    shortcode: str
    author_username: str
    url: str
    caption: Optional[str] = None
    created_at: Optional[str] = None
    processed_at: Optional[str] = None
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converts the Reel object into a dictionary."""
        return asdict(self)

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Reel":
        """Constructs a Reel object from a database Row."""
        return cls(
            id=row["id"],
            reel_id=row["reel_id"],
            shortcode=row["shortcode"],
            author_username=row["author_username"],
            caption=row["caption"],
            url=row["url"],
            created_at=row["created_at"],
            processed_at=row["processed_at"] if "processed_at" in row.keys() else None
        )
      
