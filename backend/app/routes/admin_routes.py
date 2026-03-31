from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.utils.rbac import role_required
from app.models.user_model import User

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@role_required("admin")
def list_users():
    users = [user.to_dict() for user in User.query.all()]
    return jsonify({
        "success": True,
        "data": users
    }), 200


@admin_bp.route("/stats", methods=["GET"])
@jwt_required()
@role_required("admin")
def system_stats():
    total_users = User.query.count()

    return jsonify({
        "success": True,
        "data": {
            "total_users": total_users,
            "system_status": "Operational"
        }
    }), 200