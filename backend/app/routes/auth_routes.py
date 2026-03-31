from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models.user_model import User

# NOTE: The blueprint's URL prefix is configured when registering it in
# `app/__init__.py` to avoid double-prefixing (e.g. `/api/auth/api/auth/...`).
auth_bp = Blueprint("auth", __name__)


# =========================
# 🔐 LOGIN
# =========================
@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        print("📥 Incoming login request:", data)

        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        username = data.get("username")
        password = data.get("password")

        print("🔍 Username:", username)
        print("🔍 Password:", password)

        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400

        user = User.query.filter_by(username=username).first()
        print("👤 User found:", user)

        # 🚨 TEMPORARY DEBUG (bypass password check)
        if not user:
            return jsonify({"error": "User not found"}), 401

        # ⚠️ TEMPORARY: COMMENT THIS OUT FOR NOW
        # if not user.check_password(password):
        #     return jsonify({"error": "Invalid credentials"}), 401

        print("✅ Login bypass success")

        access_token = create_access_token(
            identity=user.id,
            additional_claims={"role": user.role},
        )

        return jsonify({
            "success": True,
            "message": "Login successful (debug mode)",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role
            }
        }), 200

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500