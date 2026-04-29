from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import db
from app.models.settings_model import Settings
from app.models.user_model import User
from app.services import settings_service

settings_bp = Blueprint("settings", __name__, url_prefix="/api/settings")


# =========================
# 🔧 GET ALL SETTINGS (Organized by Category)
# =========================
@settings_bp.route("/", methods=["GET"])
@jwt_required()
def get_settings():
    """Get all settings organized by category"""
    try:
        # Initialize defaults if no settings exist
        settings_service.initialize_default_settings()
        
        # Get organized settings
        organized = settings_service.get_all_settings()
        
        return jsonify({
            "success": True,
            "data": organized
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================
# 🔧 GET SETTINGS BY CATEGORY
# =========================
@settings_bp.route("/<category>", methods=["GET"])
@jwt_required()
def get_settings_by_category(category):
    """Get settings for a specific category (scanner, ai, notification, security, system)"""
    try:
        valid_categories = ["scanner", "ai", "notification", "security", "system", "general"]
        if category not in valid_categories:
            return jsonify({
                "success": False,
                "error": f"Invalid category. Must be one of: {valid_categories}"
            }), 400
        
        settings = settings_service.get_settings_by_category(category)
        
        return jsonify({
            "success": True,
            "category": category,
            "data": settings
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================
# 🔧 UPDATE SETTINGS (Batch)
# =========================
@settings_bp.route("/", methods=["PUT"])
@jwt_required()
def update_settings():
    """Update multiple settings at once (admin only for system settings)"""
    try:
        data = request.get_json()
        claims = get_jwt()
        current_role = claims.get("role")
        current_user_id = get_jwt_identity()

        if not data or not isinstance(data, dict):
            return jsonify({
                "success": False,
                "error": "Invalid request body. Expected JSON object with settings."
            }), 400

        # Check if updating admin-only settings
        admin_only_categories = ["scanner", "ai", "system", "security"]
        restricted_keys = [
            "scan_timeout", "port_range_start", "port_range_end",
            "enable_network_scanner", "enable_web_scanner", "enable_system_scanner",
            "max_concurrent_scans", "ai_anomaly_threshold", "enable_ai_analysis",
            "enable_ai_network", "enable_ai_web", "enable_ai_system",
            "active_network_model", "active_web_model", "active_system_model",
            "session_timeout", "max_login_attempts", "require_strong_password",
            "password_min_length", "two_factor_enabled", "auto_logout",
            "dashboard_refresh_interval", "retention_days", "auto_cleanup"
        ]
        
        is_updating_admin_only = any(
            key in restricted_keys for key in data.keys()
        )
        
        if is_updating_admin_only and current_role != "admin":
            return jsonify({
                "success": False,
                "error": "Admin access required for system settings"
            }), 403

        # Update settings
        result = settings_service.update_settings_batch(data)
        
        return jsonify({
            "success": True,
            "message": "Settings updated successfully",
            "updated": result["updated"],
            "errors": result["errors"] if result["errors"] else None
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================
# 🔧 UPDATE SINGLE SETTING
# =========================
@settings_bp.route("/<key>", methods=["PUT"])
@jwt_required()
def update_single_setting(key):
    """Update a single setting by key"""
    try:
        data = request.get_json()
        claims = get_jwt()
        current_role = claims.get("role")
        
        if "value" not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'value' in request body"
            }), 400
        
        # Check admin-only settings
        restricted_keys = [
            "scan_timeout", "port_range_start", "port_range_end",
            "enable_network_scanner", "enable_web_scanner", "enable_system_scanner",
            "max_concurrent_scans", "ai_anomaly_threshold", "enable_ai_analysis",
            "enable_ai_network", "enable_ai_web", "enable_ai_system",
            "active_network_model", "active_web_model", "active_system_model",
            "session_timeout", "max_login_attempts", "require_strong_password",
            "password_min_length", "two_factor_enabled", "auto_logout",
            "dashboard_refresh_interval", "retention_days", "auto_cleanup"
        ]
        
        if key in restricted_keys and current_role != "admin":
            return jsonify({
                "success": False,
                "error": "Admin access required for this setting"
            }), 403
        
        settings_service.set_setting_value(key, data["value"])
        
        return jsonify({
            "success": True,
            "message": f"Setting '{key}' updated successfully",
            "key": key,
            "value": data["value"]
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================
# 👤 GET CURRENT USER PROFILE
# =========================
@settings_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """Get current user's profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))

        if not user:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404

        return jsonify({
            "success": True,
            "data": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "created_at": user.created_at.isoformat() if hasattr(user, 'created_at') and user.created_at else None
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================
# 👤 UPDATE PROFILE
# =========================
@settings_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """Update current user's profile (email only for non-admins)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        claims = get_jwt()
        current_role = claims.get("role")

        if not user:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404

        data = request.get_json()

        # Regular users can only update email
        if "email" in data:
            # Check if email is already taken
            existing = User.query.filter_by(email=data["email"]).first()
            if existing and existing.id != user.id:
                return jsonify({
                    "success": False,
                    "error": "Email already in use"
                }), 400
            user.email = data["email"]
        
        # Only admins can update role
        if "role" in data and current_role == "admin":
            user.role = data["role"]

        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Profile updated successfully",
            "data": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================
# 🔑 CHANGE PASSWORD
# =========================
@settings_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    """Change user's password"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        
        if not user:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get("current_password") or not data.get("new_password"):
            return jsonify({
                "success": False,
                "error": "Current password and new password are required"
            }), 400
        
        # Verify current password
        if not check_password_hash(user.password_hash, data["current_password"]):
            return jsonify({
                "success": False,
                "error": "Current password is incorrect"
            }), 401
        
        # Validate new password length
        min_length = settings_service.get_setting_value("password_min_length", 8)
        if len(data["new_password"]) < min_length:
            return jsonify({
                "success": False,
                "error": f"Password must be at least {min_length} characters long"
            }), 400
        
        # Check strong password requirement
        require_strong = settings_service.get_setting_value("require_strong_password", True)
        if require_strong:
            # At least one uppercase, one lowercase, one digit
            if not (any(c.isupper() for c in data["new_password"]) and
                    any(c.islower() for c in data["new_password"]) and
                    any(c.isdigit() for c in data["new_password"])):
                return jsonify({
                    "success": False,
                    "error": "Password must contain at least one uppercase letter, one lowercase letter, and one digit"
                }), 400
        
        # Update password
        user.password_hash = generate_password_hash(data["new_password"])
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Password changed successfully"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


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
