from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.services.dashboard_service import (
    dashboard_summary,
    asset_scan_summary,
    anomalies_by_severity,
    alerts_by_severity,
    latest_reports
)

dashboard_bp = Blueprint("dashboard_bp", __name__)

# -----------------------------
# Dashboard Summary
# -----------------------------
@dashboard_bp.route("/summary", methods=["GET"])
@jwt_required()
def get_dashboard_summary():
    """
    Returns main dashboard summary: totals and recent events
    """
    data = dashboard_summary()

    # Convert SQLAlchemy objects to dicts for recent events
    data["recent_scans"] = [
        {
            "id": scan.id,
            "asset_id": scan.asset_id,
            "status": scan.status,
            "created_at": scan.created_at.isoformat()
        } for scan in data["recent_scans"]
    ]

    data["recent_anomalies"] = [
        {
            "id": anomaly.id,
            "asset_id": anomaly.asset_id,
            "severity": anomaly.severity,
            "description": anomaly.description,
            "created_at": anomaly.created_at.isoformat()
        } for anomaly in data["recent_anomalies"]
    ]

    data["recent_alerts"] = [
        {
            "id": alert.id,
            "anomaly_id": alert.anomaly_id,
            "severity": alert.severity,
            "status": alert.status,
            "created_at": alert.created_at.isoformat()
        } for alert in data["recent_alerts"]
    ]

    return jsonify(data), 200


# -----------------------------
# Asset Scan Summary
# -----------------------------
@dashboard_bp.route("/assets", methods=["GET"])
@jwt_required()
def get_asset_scan_summary():
    """
    Returns number of scans per asset
    """
    data = asset_scan_summary()
    return jsonify(data), 200


# -----------------------------
# Anomalies by Severity
# -----------------------------
@dashboard_bp.route("/anomalies", methods=["GET"])
@jwt_required()
def get_anomalies_by_severity():
    """
    Returns anomalies grouped by severity
    """
    data = anomalies_by_severity()
    return jsonify(data), 200


# -----------------------------
# Alerts by Severity
# -----------------------------
@dashboard_bp.route("/alerts", methods=["GET"])
@jwt_required()
def get_alerts_by_severity():
    """
    Returns alerts grouped by severity
    """
    data = alerts_by_severity()
    return jsonify(data), 200


# -----------------------------
# Latest Reports
# -----------------------------
@dashboard_bp.route("/reports", methods=["GET"])
@jwt_required()
def get_latest_reports():
    """
    Returns latest reports
    """
    reports = latest_reports()
    data = [
        {
            "id": report.id,
            "name": report.name,
            "status": report.status,
            "created_at": report.created_at.isoformat()
        } for report in reports
    ]
    return jsonify(data), 200