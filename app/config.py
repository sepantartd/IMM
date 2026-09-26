"""
Configuration management module for IMM.
Loads environment variables and provides a centralized settings interface.
"""

import os
from dotenv import load_dotenv
from app.utils.security import mask_sensitive_data

# Load environment variables from .env file if present
load_dotenv()


class Config:
    """Centralized configuration class for the application."""
    
    IG_USERNAME: str = os.getenv("IG_USERNAME", "")
    IG_PASSWORD: str = os.getenv("IG_PASSWORD", "")
    
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    DRY_RUN: bool = os.getenv("DRY_RUN", "True").lower() in ("true", "1", "yes")

    @classmethod
    def validate(cls) -> bool:
        """
        Validates critical configuration parameters.
        Returns True if required credentials exist, False otherwise.
        """
        if not cls.IG_USERNAME or not cls.IG_PASSWORD:
            return False
        return True

    @classmethod
    def get_masked_summary(cls) -> dict:
        """
        Returns a dictionary of current configuration settings with secrets masked.
        Safe for logging and CLI status checks.
        """
        return {
            "IG_USERNAME": cls.IG_USERNAME if cls.IG_USERNAME else "<NOT_SET>",
            "IG_PASSWORD": mask_sensitive_data(cls.IG_PASSWORD),
            "DEBUG": cls.DEBUG,
            "DRY_RUN": cls.DRY_RUN
        }


config = Config()
