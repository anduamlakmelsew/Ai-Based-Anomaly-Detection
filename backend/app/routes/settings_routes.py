from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.database import db
from app.models import Settings

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/", methods=["GET"])
@jwt_required()
def get_settings():

    settings = Settings.query.first()

    return jsonify({
        "anomaly_threshold": settings.anomaly_threshold,
        "scan_interval": settings.scan_interval,
        "email_notifications": settings.email_notifications
    })


@settings_bp.route("/", methods=["PUT"])
@jwt_required()
def update_settings():

    data = request.get_json()

    settings = Settings.query.first()

    settings.anomaly_threshold = data["anomaly_threshold"]
    settings.scan_interval = data["scan_interval"]
    settings.email_notifications = data["email_notifications"]

    db.session.commit()

    return jsonify({"message": "Settings updated"})