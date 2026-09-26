"""
Comment generator service module for IMM.
Generates template-based or dynamic comments for target reels.
"""

import random
from typing import List, Optional
from app.models.comment import Comment
from app.models.reel import Reel
from app.utils.logger import logger


DEFAULT_TEMPLATES = [
    "عالی بود! 👌",
    "محتوای خیلی کاربردی و مفیدی بود 🔥",
    "دمت گرم @{username}، بازم از این پست‌ها بگذار 🙌",
    "خیلی جالب و آموزنده بود 👏",
    "ممنون بابت اشتراک‌گذاری این ویدیو 👍"
]


class CommentGeneratorService:
    """Service for producing contextual or template-driven comments for reels."""

    def __init__(self, templates: Optional[List[str]] = None):
        self.templates = templates if templates else DEFAULT_TEMPLATES

    def generate_comment(self, reel: Reel, custom_template: Optional[str] = None) -> Comment:
        """
        Generates a Comment object for a given Reel using specified or random template.
        """
        selected_template = custom_template or random.choice(self.templates)
        
        # Replace template placeholders if available
        final_text = selected_template.replace("{username}", reel.author_username)

        comment = Comment(
            reel_id=reel.reel_id,
            comment_text=final_text,
            status="pending"
        )

        logger.info(f"Generated comment for reel {reel.reel_id} (@{reel.author_username}): '{final_text}'")
        return comment

    def generate_batch(self, reels: List[Reel]) -> List[Comment]:
        """Generates comments for a batch of reels."""
        comments: List[Comment] = []
        for reel in reels:
            comment = self.generate_comment(reel)
            comments.append(comment)
        return comments
      
