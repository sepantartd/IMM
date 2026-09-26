"""
Delay utilities module for IMM.
Provides randomized human-like delays to prevent detection and rate-limiting.
"""

import time
import random
from app.config import config
from app.utils.logger import logger


def random_delay(min_seconds: float = 2.0, max_seconds: float = 5.0) -> float:
    """
    Pauses execution for a randomized duration between min_seconds and max_seconds.
    In DRY_RUN mode, reduces wait time significantly to speed up testing.
    """
    if config.DRY_RUN:
        delay = random.uniform(0.1, 0.3)
    else:
        delay = random.uniform(min_seconds, max_seconds)

    logger.debug(f"Applying safety delay: {delay:.2f} seconds.")
    time.sleep(delay)
    return delay
  
