"""
Configuration management module for IMM.
Loads environment variables and provides a centralized settings interface.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


class Config:
    """Centralized configuration class for the application."""
    
    IG_USERNAME: str = os.getenv("IG_USERNAME", "")
    IG_PASSWORD: str = os.getenv("IG_PASSWORD", "")
    
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    DRY_RUN: bool = os.getenv("DRY_RUN", "True").lower() in ("true", "1", "yes")

    @classmethod
    def validate(cls) -> None:
        """Validates critical configuration parameters."""
        if not cls.IG_USERNAME or not cls.IG_PASSWORD:
            # We don't raise an error immediately to allow test/dry-run modes,
            # but warnings can be handled by logging in future steps.
            pass


config = Config()
  
