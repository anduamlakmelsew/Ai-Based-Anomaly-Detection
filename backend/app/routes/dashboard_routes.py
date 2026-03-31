# app/routes/dashboard_routes.py
from flask import Blueprint, jsonify

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/summary", methods=["GET"])
def summary():

    return jsonify({
        "scans":10,
        "alerts":2,
        "anomalies":3
    })