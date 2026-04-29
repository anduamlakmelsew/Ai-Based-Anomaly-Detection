import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user_model import User
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)

# NOTE: The blueprint's URL prefix is configured when registering it in
# `app/__init__.py` to avoid double-prefixing (e.g. `/api/auth/api/auth/...`).
auth_bp = Blueprint("auth", __name__)


# =========================
# 🔐 REGISTER
# =========================
@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        logger.info("Incoming registration request")

        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        result, status_code = AuthService.register(data)
        
        if result.get("success"):
            return jsonify(result), status_code
        else:
            return jsonify(result), status_code

    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================
# 🔐 LOGIN
# =========================
@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        logger.info("Incoming login request")

        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        username = data.get("username")
        password = data.get("password")

        logger.debug(f"Login attempt for username: {username}")

        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400

        user = User.query.filter_by(username=username).first()
        logger.debug(f"User lookup result: {'found' if user else 'not found'}")

        # ✅ PROPER PASSWORD CHECK - NO MORE BYPASS
        if not user:
            return jsonify({"error": "User not found"}), 401

        if not user.check_password(password):
            logger.warning(f"Invalid password attempt for user: {username}")
            return jsonify({"error": "Invalid credentials"}), 401

        logger.info(f"Login successful for user: {username}")

        access_token = create_access_token(
            identity=str(user.id),  # Convert to string for JWT
            additional_claims={"role": user.role},
        )

        return jsonify({
            "success": True,
            "message": "Login successful",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "email": user.email
            }
        }), 200

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================
# 🔄 REFRESH TOKEN
# =========================
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Create new access token
        new_token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role}
        )

        return jsonify({
            "access_token": new_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role
            }
        }), 200

    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# =========================
# 🔑 FORGOT PASSWORD
# =========================
@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    try:
        data = request.get_json()
        logger.info("Incoming forgot password request")

        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        email = data.get("email")
        
        if not email:
            return jsonify({"error": "Email is required"}), 400

        result, status_code = AuthService.forgot_password(email)
        return jsonify(result), status_code

    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500