"""
Security Scanning Tasks

Celery temporarily disabled for stability. Can be reintroduced later for async processing.
All scans now run synchronously for improved reliability.
"""

import logging
# Celery temporarily disabled for stability
# from celery import shared_task
# from celery.exceptions import SoftTimeLimitExceeded
from sqlalchemy.exc import SQLAlchemyError

# Import the actual scan execution logic
from app.services.scan_service import (
    run_network_scan_task,
    run_web_scan_task,
    run_system_scan_task,
    emit_scan_progress
)

logger = logging.getLogger(__name__)


def run_security_scan(scan_id, target, scan_type, user_id=None, options=None):
    """
    Execute a security scan synchronously.
    
    Celery temporarily disabled for stability. Can be reintroduced later for async processing.
    All scans now run synchronously for improved reliability.
    
    Args:
        scan_id: The database scan record ID
        target: Target host/network to scan
        scan_type: Type of scan (network, web, system)
        user_id: ID of user who initiated the scan
        options: Additional scan options dict
    
    Returns:
        dict: Scan results summary
    """
    logger.info(f"Starting {scan_type} scan on {target} (scan_id={scan_id})")
    
    # Import models here to ensure Flask app context is available
    from app.models.scan_model import Scan
    from app import db
    
    scan = None
    
    try:
        # Get scan record with row locking to prevent race conditions
        # Uses SELECT FOR UPDATE to lock the row during scan execution
        scan = db.session.query(Scan).filter_by(id=scan_id).with_for_update().first()
        
        if not scan:
            raise ValueError(f"Scan {scan_id} not found")
        
        # Check if scan is already being processed by another worker
        if scan.status == "running":
            logger.warning(f"Scan {scan_id} already running, aborting duplicate")
            raise ValueError(f"Scan already running")
        
        # Update scan status to running
        scan.status = "running"
        db.session.commit()
        
        # Refresh scan object after commit to ensure we have latest data
        db.session.refresh(scan)
        
        # Emit initial progress
        emit_scan_progress(scan_id, 0, "running", "Initializing scan")
        
        # Execute the appropriate scan based on type
        if scan_type == "network":
            result = run_network_scan_task(scan_id, target, user_id)
        elif scan_type == "web":
            result = run_web_scan_task(scan_id, target, user_id)
        elif scan_type == "system":
            result = run_system_scan_task(scan_id, target, user_id)
        else:
            raise ValueError(f"Unknown scan type: {scan_type}")
        
        # Re-acquire lock for final update
        scan = db.session.query(Scan).filter_by(id=scan_id).with_for_update().first()
        if scan:
            # Update scan with results
            scan.set_result(result)
            db.session.commit()
        
        # Emit completion
        emit_scan_progress(scan_id, 100, "completed", "Scan completed")
        
        logger.info(f"Scan {scan_id} completed successfully")
        
        return {
            "success": True,
            "scan_id": scan_id,
            "target": target,
            "scan_type": scan_type,
            "status": "completed",
            "result": result
        }
        
    except Exception as exc:
        logger.exception(f"Scan failed: {exc}")
        # Mark as failed immediately
        _handle_scan_failure(scan_id, str(exc), None, is_final=True)
        raise


def _handle_scan_failure(scan_id: int, error_message: str, task_id: str, is_timeout: bool = False, is_final: bool = False):
    """
    Helper function to consistently handle scan failures.
    
    Args:
        scan_id: The scan database ID
        error_message: Error message to store
        task_id: The Celery task ID
        is_timeout: Whether this was a timeout failure
        is_final: Whether this is the final retry (no more retries)
    """
    try:
        from app.models.scan_model import Scan
        from app import db
        
        # Get scan with lock
        scan = db.session.query(Scan).filter_by(id=scan_id).with_for_update().first()
        if scan:
            scan.mark_failed(error_message)
            scan.celery_task_id = task_id  # Keep task ID for debugging
            db.session.commit()
            
            status = "timed out" if is_timeout else "failed"
            if is_final:
                status += " (final)"
            
            emit_scan_progress(scan_id, 100, "failed", f"Error: {error_message}")
            logger.info(f"[Celery Task {task_id}] Scan {scan_id} marked as {status}")
    except Exception as cleanup_error:
        logger.error(f"[Celery Task {task_id}] Failed to cleanup failed scan {scan_id}: {cleanup_error}")


# Celery temporarily disabled for stability. Can be reintroduced later for async processing.
# The following periodic tasks are disabled:
# - cleanup_stale_scans
# - notify_scan_completion
# 
# These can be re-enabled by uncommenting and adding @shared_task decorators back.
