from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models.users_model import User


def admin_required(fn):
    """
    Allows only admin users.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):

        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.role != "admin":
            return jsonify({"error": "Admin access required"}), 403

        return fn(*args, **kwargs)

    return wrapper