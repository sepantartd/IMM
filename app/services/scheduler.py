"""
Daemon & Scheduler service module for IMM.
Runs the automation pipeline periodically in a background loop with graceful shutdown handling.
"""

import time
import signal
from typing import Dict, Any, Optional
from app.services.pipeline import AutomationPipeline
from app.utils.logger import logger


class DaemonScheduler:
    """Handles periodic scheduled execution of the IMM automation pipeline."""

    def __init__(self, interval_minutes: int = 30):
        self.interval_seconds = max(1, interval_minutes) * 60
        self.running = False
        self.pipeline: Optional[AutomationPipeline] = None
        self._setup_signal_handlers()

    def _setup_signal_handlers(self) -> None:
        """Configures OS signal handling for graceful shutdown (Ctrl+C / SIGTERM)."""
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame) -> None:
        """Signal handler to stop daemon loop cleanly."""
        logger.info("Shutdown signal received. Stopping IMM Daemon...")
        self.running = False

    def start(
        self,
        target: str,
        mode: str = "username",
        limit: int = 5,
        criteria: Optional[Dict[str, Any]] = None,
        auto_submit: bool = False
    ) -> None:
        """
        Starts the daemon execution loop.
        Runs pipeline discovery and optionally submits approved comments every interval.
        """
        self.running = True
        self.pipeline = AutomationPipeline()
        logger.info(f"IMM Daemon started. Target: '{target}', Interval: {self.interval_seconds // 60}m")

        cycle_count = 0

        try:
            while self.running:
                cycle_count += 1
                logger.info(f"=== Starting Daemon Cycle #{cycle_count} ===")

                # 1. Run Discovery & Comment Generation
                gen_stats = self.pipeline.run_discovery_and_generation(
                    target=target,
                    mode=mode,
                    limit=limit,
                    criteria=criteria
                )
                logger.info(f"Cycle #{cycle_count} Generation Stats: {gen_stats}")

                # 2. Process Approved Submissions if enabled
                if auto_submit:
                    sub_stats = self.pipeline.process_approved_submissions(batch_limit=limit)
                    logger.info(f"Cycle #{cycle_count} Submission Stats: {sub_stats}")

                logger.info(f"Cycle #{cycle_count} finished. Sleeping for {self.interval_seconds // 60} minutes...")

                # Sleep in short increments to respond quickly to shutdown signals
                sleep_counter = 0
                while self.running and sleep_counter < self.interval_seconds:
                    time.sleep(1)
                    sleep_counter += 1

        except Exception as e:
            logger.error(f"Daemon encountered an unhandled exception: {e}")
        finally:
            if self.pipeline:
                self.pipeline.close()
            logger.info("IMM Daemon stopped successfully.")
