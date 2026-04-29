"""
Notification Service - Minimal safe implementation

Celery temporarily disabled for stability. Can be reintroduced later for async processing.
This is a fallback implementation to prevent import errors.
"""

import logging

logger = logging.getLogger(__name__)


def emit_scan_progress(scan_id, progress, status, message=None):
    """
    Emit scan progress notification.
    
    Temporary fallback implementation (no websocket / socketio dependency).
    Logs progress to console for debugging.
    """
    msg = f"[SCAN PROGRESS] id={scan_id}, progress={progress}%, status={status}"
    if message:
        msg += f", message={message}"
    logger.info(msg)
    print(msg)


def notify_scan_complete(scan_id, status, result=None):
    """
    Notify that a scan has completed.
    
    Temporary fallback implementation.
    """
    msg = f"[SCAN COMPLETE] id={scan_id}, status={status}"
    logger.info(msg)
    print(msg)
