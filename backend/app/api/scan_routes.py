from flask import Blueprint, request, jsonify

from app.scanner.network.service import run_network_scan
from app.scanner.web.service import run_web_scan
from app.scanner.system.service import run_system_scan

scan_bp = Blueprint("scan", __name__)


@scan_bp.route("/scan/network", methods=["POST"])
def network_scan():

    data = request.get_json()
    target = data.get("target")

    if not target:
        return jsonify({
            "success": False,
            "message": "Target is required"
        }), 400

    result = run_network_scan(target)

    return jsonify(result)


@scan_bp.route("/scan/web", methods=["POST"])
def web_scan():

    data = request.get_json()
    target = data.get("target")

    if not target:
        return jsonify({
            "success": False,
            "message": "Target is required"
        }), 400

    result = run_web_scan(target)

    return jsonify(result)


@scan_bp.route("/scan/system", methods=["POST"])
def system_scan():

    data = request.get_json()
    target = data.get("target")

    result, risk = run_system_scan(target)

    return jsonify(result)