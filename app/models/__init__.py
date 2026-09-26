"""
Data models package initialization for IMM.
Exposes core entities for cleaner imports.
"""

from app.models.reel import Reel
from app.models.comment import Comment

__all__ = ["Reel", "Comment"]
