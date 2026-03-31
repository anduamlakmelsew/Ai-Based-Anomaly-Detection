from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.rbac import role_required

analyst_bp = Blueprint("analyst", __name__, url_prefix="/api/analyst")


@analyst_bp.route("/dashboard", methods=["GET"])
@jwt_required()
@role_required("analyst")
def analyst_dashboard():
    user_id = get_jwt_identity()

    return jsonify({
        "success": True,
        "data": {
            "message": "Welcome Analyst",
            "user_id": user_id
        }
    }), 200