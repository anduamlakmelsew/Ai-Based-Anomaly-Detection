import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.scan_model import Scan
# Celery temporarily disabled for stability. Can be reintroduced later for async processing.
from app.tasks.scan_tasks import run_security_scan
from app.services.notification_service import emit_scan_progress
from app.services.scan_service import run_scan, get_scan_history, get_celery_task_status
from app.scanner.network.discovery import discover_hosts
from datetime import datetime
from app.utils.audit_logger import log_action
from app.models.ai_detection_event_model import AIDetectionEvent
from app import db

# Import AI pipeline for manual testing
try:
    from app.ai.pipeline import run_manual_ai_test
except ImportError:
    run_manual_ai_test = None

# All scans now run synchronously for improved reliability.
CELERY_AVAILABLE = False

logger = logging.getLogger(__name__)

scan_bp = Blueprint("scan", __name__, url_prefix="/api/scan")


# =========================
# 🚀 START SCAN (ASYNC with Celery)
# =========================
@scan_bp.route("/start", methods=["POST"])
@jwt_required()
def start_scan():
    """
    Start a security scan asynchronously using Celery.
    
    Instead of running the scan directly, this endpoint:
    1. Creates a scan record in the database with 'queued' status
    2. Enqueues a Celery task to execute the scan in the background
    3. Returns immediately with the scan_id and celery_task_id
    
    The frontend can then:
    - Poll /api/scan/status/<task_id> for progress
    - Listen to WebSocket 'scan_progress' events for real-time updates
    - Fetch results from /api/scan/<scan_id> when complete
    """
    try:
        data = request.get_json()
        target = data.get("target")
        scan_type = data.get("scan_type", "web")
        sync_mode = data.get("sync", False)  # Optional: run synchronously for testing

        if not target:
            return jsonify({"error": "Target is required"}), 400

        # ✅ GET USER
        user_id = int(get_jwt_identity())

        # 📝 AUDIT LOG
        log_action(
            action="scan_started",
            user_id=user_id,
            description=f"Scan queued on target {target} with type {scan_type}",
        )

        # Create scan record with 'queued' status
        scan = Scan(
            target=target,
            scan_type=scan_type,
            status="queued",
            progress=0,
            user_id=user_id
        )
        db.session.add(scan)
        db.session.commit()

        # ✅ SYNC MODE (for testing/development)
        if sync_mode or run_security_scan is None:
            logger.info(f"Running scan {scan.id} synchronously (sync_mode={sync_mode}, celery_available={run_security_scan is not None})")
            result = run_scan(target, scan_type, user_id)
            return jsonify({
                "success": True,
                "message": "Scan completed (synchronous mode)",
                "scan_id": scan.id,
                "data": result
            })

        # Run scan synchronously (Celery temporarily disabled for stability)
        try:
            # Call scan function directly without Celery
            result = run_security_scan(
                scan_id=scan.id,
                target=data.get("target", ""),
                scan_type=scan_type,
                user_id=user_id,
                options=data.get("options", {})
            )
            
            return jsonify({
                "success": True,
                "scan_id": scan.id,
                "status": "completed" if result else "failed",
                "message": "Scan completed successfully" if result else "Scan failed",
                "estimated_duration": "2-5 minutes"
            }), 200
            
        except Exception as e:
            logger.error(f"Failed to execute scan: {e}")
            scan.status = "failed"
            scan.error_message = f"Scan execution failed: {str(e)}"
            db.session.commit()
            
            return jsonify({
                "success": False,
                "scan_id": scan.id,
                "error": "Failed to execute scan",
                "message": str(e)
            }), 500

    except Exception as e:
        logger.error(f"Failed to start scan: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to start scan",
            "message": str(e)
        }), 500


# =========================
# 📜 SCAN HISTORY
# =========================
@scan_bp.route("/history", methods=["GET"])
@jwt_required()
def scan_history():
    try:
        user_id = int(get_jwt_identity())  # Convert string back to int

        history = get_scan_history(user_id)

        return jsonify({
            "success": True,
            "data": history
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================
# 🌐 NETWORK DISCOVERY
# =========================
@scan_bp.route("/discover", methods=["POST"])
@jwt_required()
def discover():
    """
    Run a lightweight network discovery (ping scan) for a CIDR range,
    e.g. 192.168.1.0/24, and return the list of live hosts.
    """
    try:
        data = request.get_json() or {}
        target = data.get("target")

        if not target:
            return jsonify({"success": False, "error": "Target range is required"}), 400

        result = discover_hosts(target)
        return jsonify(result), (200 if result.get("success") else 500)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================
# 🔍 GET SINGLE SCAN
# =========================
@scan_bp.route("/<int:scan_id>", methods=["GET"])
@jwt_required()
def get_scan(scan_id):
    try:
        user_id = int(get_jwt_identity())  # Convert string back to int

        from app.models.scan_model import Scan

        scan = Scan.query.filter_by(id=scan_id, user_id=user_id).first()

        if not scan:
            return jsonify({
                "success": False,
                "error": "Scan not found"
            }), 404

        return jsonify({
            "success": True,
            "data": scan.result
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================
# 🧠 AI DETECTION EVENTS HISTORY
# =========================
@scan_bp.route("/history/ai", methods=["GET"])
@jwt_required()
def ai_detection_history():
    """
    Get AI detection events history.
    Returns the last 100 AI analysis events with risk levels and predictions.
    """
    try:
        user_id = int(get_jwt_identity())
        limit = request.args.get('limit', 100, type=int)
        source_type = request.args.get('source_type', None)
        
        # Get events from database
        events = AIDetectionEvent.get_recent_events(
            limit=limit,
            user_id=user_id,
            source_type=source_type
        )
        
        # Convert to dashboard format
        result = [event.to_dashboard_format() for event in events]
        
        return jsonify({
            "success": True,
            "data": result,
            "count": len(result)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================
# 🧠 AI DETECTION STATISTICS
# =========================
@scan_bp.route("/history/ai/stats", methods=["GET"])
@jwt_required()
def ai_detection_stats():
    """
    Get AI detection statistics for dashboard.
    Returns risk distribution and counts by source type.
    """
    try:
        user_id = int(get_jwt_identity())
        hours = request.args.get('hours', 24, type=int)
        
        # Get statistics
        stats = AIDetectionEvent.get_risk_stats(
            hours=hours,
            user_id=user_id
        )
        
        # Get critical events for alerts
        critical_events = AIDetectionEvent.get_critical_events(
            limit=10,
            user_id=user_id
        )
        
        return jsonify({
            "success": True,
            "data": {
                "stats": stats,
                "critical_events": [event.to_dashboard_format() for event in critical_events]
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================
# 📊 SCAN STATUS (Celery Task Status)
# =========================
@scan_bp.route("/status/<task_id>", methods=["GET"])
@jwt_required()
def get_scan_status(task_id):
    """
    Get the status of a Celery scan task.
    
    Returns:
        - task state (PENDING, STARTED, PROGRESS, SUCCESS, FAILURE)
        - progress percentage (if available)
        - current stage description
        - result (if task completed)
        - error (if task failed)
    
    Use this endpoint to poll for scan progress from the frontend.
    """
    try:
        user_id = int(get_jwt_identity())
        
        # Get Celery task status
        task_status = get_celery_task_status(task_id)
        
        # Find associated scan record
        scan = Scan.query.filter_by(celery_task_id=task_id, user_id=user_id).first()
        
        if not scan:
            # Task might exist but not belong to this user
            return jsonify({
                "success": False,
                "error": "Scan not found or access denied"
            }), 404
        
        response = {
            "success": True,
            "scan_id": scan.id,
            "celery_task_id": task_id,
            "task_state": task_status["state"],
            "ready": task_status["ready"],
            "successful": task_status.get("successful"),
            "target": scan.target,
            "scan_type": scan.scan_type,
            "created_at": scan.created_at.isoformat() if scan.created_at else None,
        }
        
        # Add progress info if available
        if "progress" in task_status:
            response["progress"] = task_status["progress"]
        if "stage" in task_status:
            response["stage"] = task_status["stage"]
        
        # Add scan status from database
        response["scan_status"] = scan.status
        
        # Add result if task is complete
        if task_status["ready"]:
            if task_status.get("successful"):
                response["result"] = task_status.get("result")
            else:
                response["error"] = task_status.get("error")
        
        return jsonify(response)
        
    except Exception as e:
        logger.exception(f"Failed to get scan status for task {task_id}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================
# 🧠 AI SECURITY LAB - MANUAL TEST
# =========================
@scan_bp.route("/ai/test", methods=["POST"])
@jwt_required()
def ai_manual_test():
    """
    Manual AI testing endpoint for AI Security Lab.
    Accepts network, system, and web data for unified AI analysis.
    
    Request body:
    {
        "network": { "duration": 1.0, "src_bytes": 1000, ... },
        "system": { "cpu_usage": 50.0, "memory_usage": 60.0, ... },
        "web": { "url": "/test", "payload": "<script>..." }
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        
        # Log the test action
        log_action(
            action="ai_manual_test",
            user_id=user_id,
            description="User ran manual AI test from AI Security Lab"
        )
        
        # Extract input data
        network_data = data.get("network")
        system_data = data.get("system")
        web_data = data.get("web")
        
        # Validate that at least one data type is provided
        if not any([network_data, system_data, web_data]):
            return jsonify({
                "success": False,
                "error": "At least one of network, system, or web data must be provided"
            }), 400
        
        # Run AI test
        if run_manual_ai_test:
            result = run_manual_ai_test(
                user_id=user_id,
                network_data=network_data,
                system_data=system_data,
                web_data=web_data
            )
            
            return jsonify({
                "success": True,
                "data": result
            })
        else:
            return jsonify({
                "success": False,
                "error": "AI test service not available"
            }), 503
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500