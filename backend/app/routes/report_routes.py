from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.models import Report

report_bp = Blueprint("reports", __name__)


@report_bp.route("/", methods=["GET"])
@jwt_required()
def get_reports():

    reports = Report.query.all()

    result = []

    for r in reports:
        result.append({
            "id": r.id,
            "report_type": r.report_type,
            "generated_at": r.generated_at,
            "file_path": r.file_path
        })

    return jsonify(result)


@report_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate_report():

    # For now dummy logic
    report = Report(
        report_type="scan_report",
        file_path="reports/report1.pdf"
    )

    db.session.add(report)
    db.session.commit()

    return jsonify({"message": "Report generated"})