from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.scan_model import Scan
from .service import run_scan

scanner_bp = Blueprint("scanner", __name__, url_prefix="/api/scanner")


# =========================
# 🔹 RUN NETWORK ONLY
# =========================
@scanner_bp.route("/network", methods=["POST"])
@jwt_required()
def network_scan():
    data = request.get_json()
    target = data.get("target")

    if not target:
        return jsonify({"success": False, "message": "Target required"}), 400

    result = run_scan("network", target)

    return jsonify(result)


# =========================
# 🔹 RUN SCAN (MAIN ENTRY)
# =========================
@scanner_bp.route("/run", methods=["POST"])
@jwt_required()
def run():
    data = request.get_json()

    scan_type = data.get("scan_type")
    target = data.get("target")
    user_id = int(get_jwt_identity())

    if not scan_type or not target:
        return jsonify({
            "success": False,
            "message": "scan_type and target required"
        }), 400

    # -----------------------------
    # 1. CREATE SCAN (QUEUED)
    # -----------------------------
    scan = Scan(
        scan_type=scan_type,
        target=target,
        user_id=user_id,
        status="running",
        progress=10
    )

    db.session.add(scan)
    db.session.commit()

    try:
        # -----------------------------
        # 2. RUN SCAN
        # -----------------------------
        result = run_scan(scan_type, target)

        if not result.get("success"):
            scan.mark_failed(result.get("message", "Scan failed"))
            db.session.commit()
            return jsonify(result), 400

        # -----------------------------
        # 3. SAVE RESULT (🔥 IMPORTANT)
        # -----------------------------
        scan.set_result(result)

        db.session.commit()

        return jsonify(result)

    except Exception as e:
        scan.mark_failed(str(e))
        db.session.commit()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# =========================
# 🔹 SCAN HISTORY (🔥 DASHBOARD)
# =========================
@scanner_bp.route("/history", methods=["GET"])
@jwt_required()
def history():
    user_id = int(get_jwt_identity())

    scans = Scan.query.filter_by(user_id=user_id) \
        .order_by(Scan.created_at.desc()) \
        .all()

    return jsonify([s.to_dict() for s in scans])


# =========================
# 🔹 GET SINGLE SCAN
# =========================
@scanner_bp.route("/<int:scan_id>", methods=["GET"])
@jwt_required()
def get_scan(scan_id):
    user_id = int(get_jwt_identity())

    scan = Scan.query.filter_by(id=scan_id, user_id=user_id).first()

    if not scan:
        return jsonify({
            "success": False,
            "message": "Scan not found"
        }), 404

    return jsonify(scan.to_dict())