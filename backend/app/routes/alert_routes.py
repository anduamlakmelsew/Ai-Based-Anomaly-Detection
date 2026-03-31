from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.models.alert_model import Alert
from app.services.alert_service import create_alert, delete_alert, get_alert, list_alerts


alert_bp = Blueprint("alerts", __name__, url_prefix="/api/alerts")


@alert_bp.route("/", methods=["GET"])
@jwt_required()
def get_alerts():
    alerts = list_alerts()
    return jsonify([a.to_dict() for a in alerts]), 200


@alert_bp.route("/<int:alert_id>", methods=["GET"])
@jwt_required()
def alert_details(alert_id):
    alert = get_alert(alert_id)
    if not alert:
        return jsonify({"error": "Alert not found"}), 404
    return jsonify(alert.to_dict()), 200


@alert_bp.route("/<int:alert_id>/resolve", methods=["PUT"])
@jwt_required()
def resolve_alert_route(alert_id):
    alert = get_alert(alert_id)
    if not alert:
        return jsonify({"error": "Alert not found"}), 404

    alert.status = "resolved"
    from app import db

    db.session.commit()
    return jsonify(alert.to_dict()), 200