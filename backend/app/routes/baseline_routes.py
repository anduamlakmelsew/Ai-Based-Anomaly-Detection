from flask import Blueprint, request, jsonify
from app import db
from app.models import Baseline
from flask_jwt_extended import jwt_required, get_jwt_identity

baseline_bp = Blueprint("baseline", __name__, url_prefix="/api/baseline")

@baseline_bp.route("/scan", methods=["POST"])
@jwt_required()
def scan_baseline():
    current_user = get_jwt_identity()
    data = request.json
    # Example: save scan request
    baseline = Baseline(user_id=current_user, target_ip=data["target_ip"])
    db.session.add(baseline)
    db.session.commit()
    # Here you would trigger your scanning logic asynchronously
    return jsonify({"msg": "Scan started", "baseline_id": baseline.id})