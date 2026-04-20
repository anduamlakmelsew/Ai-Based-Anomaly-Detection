from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.scan_service import run_scan, get_scan_history
from app.scanner.network.discovery import discover_hosts
from app.utils.audit_logger import log_action

scan_bp = Blueprint("scan", __name__, url_prefix="/api/scan")


# =========================
# 🚀 START SCAN
# =========================
@scan_bp.route("/start", methods=["POST"])
@jwt_required()
def start_scan():
    try:
        data = request.get_json()
        target = data.get("target")
        scan_type = data.get("scan_type", "web")

        if not target:
            return jsonify({"error": "Target is required"}), 400

        # ✅ GET USER
        user_id = int(get_jwt_identity())  # Convert string back to int

        # 📝 AUDIT LOG — user started a scan
        log_action(
            action="scan_started",
            user_id=user_id,
            description=f"Scan started on target {target} with type {scan_type}",
        )

        # ✅ RUN SCAN (FIXED)
        result = run_scan(target, scan_type, user_id)

        return jsonify({
            "success": True,
            "message": "Scan completed",
            "data": result
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
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