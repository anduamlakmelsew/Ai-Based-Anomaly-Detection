from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.models import Anomaly

anomaly_bp = Blueprint("anomalies", __name__)

@anomaly_bp.route("/", methods=["GET"])
@jwt_required()
def get_anomalies():
    
    anomalies = Anomaly.query.all()

    result = []

    for a in anomalies:
        result.append({
            "id": a.id,
            "scan_id": a.scan_id,
            "metric_name": a.metric_name,
            "expected_value": a.expected_value,
            "actual_value": a.actual_value,
            "severity": a.severity
        })

    return jsonify(result)


@anomaly_bp.route("/<int:id>", methods=["GET"])
@jwt_required()
def get_anomaly(id):

    anomaly = Anomaly.query.get_or_404(id)

    return jsonify({
        "id": anomaly.id,
        "scan_id": anomaly.scan_id,
        "metric_name": anomaly.metric_name,
        "expected_value": anomaly.expected_value,
        "actual_value": anomaly.actual_value,
        "severity": anomaly.severity
    })