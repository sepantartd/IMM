"""
Services package initialization for IMM.
Exposes core business logic services.
"""

from app.services.discovery import ReelDiscoveryService
from app.services.filter_service import ReelFilterService
from app.services.deduplication import DeduplicationService
from app.services.comment_generator import CommentGeneratorService
from app.services.approval import ApprovalService
from app.services.submission_service import SubmissionService
from app.services.rate_limiter import RateLimiterService
from app.services.list_service import ListService
from app.services.pipeline import AutomationPipeline
from app.services.scheduler import DaemonScheduler
from app.services.analytics import AnalyticsService
from app.services.health_check import HealthCheckService
from app.services.backup_service import DatabaseBackupService
from app.services.proxy_manager import ProxyManagerService

__all__ = [
    "ReelDiscoveryService",
    "ReelFilterService",
    "DeduplicationService",
    "CommentGeneratorService",
    "ApprovalService",
    "SubmissionService",
    "RateLimiterService",
    "ListService",
    "AutomationPipeline",
    "DaemonScheduler",
    "AnalyticsService",
    "HealthCheckService",
    "DatabaseBackupService",
    "ProxyManagerService"
]
