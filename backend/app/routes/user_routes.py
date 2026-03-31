from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.user_model import User

user_bp = Blueprint("users", __name__, url_prefix="/api/users")


# =========================
# 👥 GET ALL USERS (PROTECTED)
# =========================
@user_bp.route("/", methods=["GET"])
@jwt_required()
def get_users():
    users = User.query.all()

    result = []
    for u in users:
        result.append({
            "id": u.id,
            "username": u.username,
            "role": u.role
        })

    return jsonify(result)


# =========================
# ➕ CREATE USER (PUBLIC - TEMP)
# =========================
@user_bp.route("/", methods=["POST"])
def create_user():
    try:
        data = request.get_json()

        username = data.get("username")
        password = data.get("password")
        role = data.get("role", "user")

        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400

        # 🔍 Prevent duplicate user
        existing = User.query.filter_by(username=username).first()
        if existing:
            return jsonify({"error": "User already exists"}), 400

        # ✅ CREATE USER CORRECTLY
        user = User(
            username=username,
            role=role
        )
        user.set_password(password)  # 🔥 CORRECT PASSWORD HANDLING

        db.session.add(user)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "User created"
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================
# ❌ DELETE USER (PROTECTED)
# =========================
@user_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_user(id):
    user = User.query.get_or_404(id)

    db.session.delete(user)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "User deleted"
    })