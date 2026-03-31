from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.log_model import Log


audit_bp = Blueprint("audit", __name__, url_prefix="/api/audit")


@audit_bp.route("/logs", methods=["GET"])
@jwt_required()
def get_logs():
  """
  Return recent audit log entries for the current user.
  """
  user_id = int(get_jwt_identity())

  logs = (
      Log.query.filter_by(user_id=user_id)
      .order_by(Log.created_at.desc())
      .limit(50)
      .all()
  )

  return jsonify([log.to_dict() for log in logs]), 200

