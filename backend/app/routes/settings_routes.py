from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.database import db
from app.models import Settings
from app.models.user_model import User

settings_bp = Blueprint("settings", __name__)


# =========================
# 🔧 GET ALL SETTINGS
# =========================
@settings_bp.route("/", methods=["GET"])
@jwt_required()
def get_settings():
    settings = Settings.query.all()
    result = {}
    for s in settings:
        result[s.key] = s.value

    # Return defaults if no settings exist
    defaults = {
        "anomaly_threshold": result.get("anomaly_threshold", "75"),
        "scan_interval": result.get("scan_interval", "60"),
        "email_notifications": result.get("email_notifications", "true"),
        "report_notifications": result.get("report_notifications", "true"),
        "alert_notifications": result.get("alert_notifications", "true"),
        "auto_scan": result.get("auto_scan", "false"),
        "retention_days": result.get("retention_days", "90"),
        "session_timeout": result.get("session_timeout", "60"),
        "max_login_attempts": result.get("max_login_attempts", "5"),
        "require_strong_password": result.get("require_strong_password", "true"),
    }
    return jsonify(defaults)


# =========================
# 🔧 UPDATE SETTINGS
# =========================
@settings_bp.route("/", methods=["PUT"])
@jwt_required()
def update_settings():
    try:
        data = request.get_json()
        claims = get_jwt()
        current_role = claims.get("role")

        # Only admin can update system settings
        if current_role != "admin":
            return jsonify({"error": "Admin access required"}), 403

        for key, value in data.items():
            setting = Settings.query.filter_by(key=key).first()
            if setting:
                setting.value = str(value)
            else:
                setting = Settings(key=key, value=str(value))
                db.session.add(setting)

        db.session.commit()
        return jsonify({"success": True, "message": "Settings updated successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# =========================
# 👤 GET CURRENT USER PROFILE
# =========================
@settings_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    })


# =========================
# 👤 UPDATE PROFILE
# =========================
@settings_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))

        if not user:
            return jsonify({"error": "User not found"}), 404

        data = request.get_json()

        if "email" in data:
            user.email = data["email"]

        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Profile updated successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# =========================
# 📊 GET SYSTEM STATUS
# =========================
@settings_bp.route("/system-status", methods=["GET"])
@jwt_required()
def get_system_status():
    try:
        claims = get_jwt()
        current_role = claims.get("role")

        # Only admin can see system status
        if current_role != "admin":
            return jsonify({"error": "Admin access required"}), 403

        # Get system info
        total_users = User.query.count()
        db_status = "Connected" if db.session else "Disconnected"

        return jsonify({
            "success": True,
            "data": {
                "database_status": db_status,
                "total_users": total_users,
                "system_status": "Operational",
                "version": "1.0.0"
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
