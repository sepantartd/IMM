"""
Logging system module for IMM.
Configures file and console loggers for tracking application operations and errors.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from app.config import config


LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
LOG_FILE_PATH = os.path.join(LOGS_DIR, "app.log")


def setup_logger(name: str = "IMM") -> logging.Logger:
    """
    Sets up and returns a configured Logger instance.
    Writes logs to both console and logs/app.log file.
    """
    os.makedirs(LOGS_DIR, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if config.DEBUG else logging.INFO)

    # Prevent duplicate handlers if setup_logger is called multiple times
    if logger.handlers:
        return logger

    # Log Formatter
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File Handler (Max 5MB per file, keeping 3 backup files)
    file_handler = RotatingFileHandler(
        LOG_FILE_PATH,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if config.DEBUG else logging.INFO)
    console_handler.setFormatter(formatter)

    # Add Handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Global default logger instance
logger = setup_logger()
  
