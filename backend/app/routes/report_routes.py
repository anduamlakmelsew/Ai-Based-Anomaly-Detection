from flask import Blueprint, jsonify, request, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import csv
import json
import io
from datetime import datetime

from app.models.scan_model import Scan
from app.models.report_model import Report
from app import db

# Import PDF generator
try:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from automation.pdf_generator import generate_scan_report, generate_consolidated_report
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

report_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


@report_bp.route("/", methods=["GET"])
@jwt_required()
def get_reports():
    """Get all generated reports for user"""
    try:
        user_id = int(get_jwt_identity())
        reports = Report.query.filter_by(user_id=user_id).order_by(Report.generated_at.desc()).all()
        
        return jsonify({
            "success": True,
            "data": [
                {
                    "id": r.id,
                    "report_type": r.report_type,
                    "generated_at": r.generated_at.isoformat() if r.generated_at else None,
                    "file_path": r.file_path,
                    "file_size": r.file_size
                }
                for r in reports
            ]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@report_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate_report():
    """Generate PDF report for scans"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        
        scan_ids = data.get("scan_ids", [])
        report_type = data.get("report_type", "single")  # single or consolidated
        
        if not PDF_AVAILABLE:
            return jsonify({
                "success": False,
                "error": "PDF generation not available. Install reportlab."
            }), 503
        
        # Get scans
        scans = Scan.query.filter(
            Scan.id.in_(scan_ids),
            Scan.user_id == user_id
        ).all()
        
        if not scans:
            return jsonify({
                "success": False,
                "error": "No scans found for provided IDs"
            }), 404
        
        # Generate report
        reports_dir = os.path.join(current_app.root_path, '..', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        if report_type == "consolidated" and len(scans) > 1:
            scans_data = [s.result for s in scans if s.result]
            output_path = generate_consolidated_report(scans_data, reports_dir)
        else:
            # Generate for first scan
            scan = scans[0]
            output_path = generate_scan_report(scan.result or {}, reports_dir)
        
        # Save report record
        report = Report(
            report_type=report_type,
            file_path=output_path,
            file_size=os.path.getsize(output_path) if os.path.exists(output_path) else 0,
            user_id=user_id
        )
        db.session.add(report)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Report generated successfully",
            "data": {
                "report_id": report.id,
                "file_path": output_path,
                "download_url": f"/api/reports/download/{report.id}"
            }
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@report_bp.route("/download/<int:report_id>", methods=["GET"])
@jwt_required()
def download_report(report_id):
    """Download a generated report"""
    try:
        user_id = int(get_jwt_identity())
        report = Report.query.filter_by(id=report_id, user_id=user_id).first_or_404()
        
        if not os.path.exists(report.file_path):
            return jsonify({"success": False, "error": "File not found"}), 404
        
        return send_file(
            report.file_path,
            as_attachment=True,
            download_name=os.path.basename(report.file_path)
        )
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@report_bp.route("/export/<format>", methods=["GET"])
@jwt_required()
def export_data(format):
    """Export scan data in various formats (csv, json)"""
    try:
        user_id = int(get_jwt_identity())
        format = format.lower()
        
        if format not in ["csv", "json"]:
            return jsonify({
                "success": False,
                "error": "Invalid format. Use 'csv' or 'json'"
            }), 400
        
        # Get user's scans
        scans = Scan.query.filter_by(user_id=user_id).order_by(Scan.created_at.desc()).all()
        
        if format == "csv":
            return _export_csv(scans)
        else:
            return _export_json(scans)
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def _export_csv(scans):
    """Export scans to CSV format"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'Scan ID', 'Target', 'Scan Type', 'Status', 'Risk Score',
        'Risk Level', 'Findings Count', 'Timestamp', 'AI Prediction'
    ])
    
    # Data rows
    for scan in scans:
        result = scan.result or {}
        data = result.get("data", {})
        risk = data.get("risk_analysis", {})
        ai = result.get("ai_analysis", {})
        findings = data.get("findings", [])
        
        writer.writerow([
            scan.id,
            scan.target,
            scan.scan_type,
            scan.status,
            risk.get("total_risk_score", 0),
            risk.get("risk_level", "UNKNOWN"),
            len(findings),
            scan.created_at.isoformat() if scan.created_at else "",
            ai.get("prediction", "unknown")
        ])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'scans_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )


def _export_json(scans):
    """Export scans to JSON format"""
    data = []
    
    for scan in scans:
        result = scan.result or {}
        
        data.append({
            "id": scan.id,
            "target": scan.target,
            "scan_type": scan.scan_type,
            "status": scan.status,
            "risk_score": scan.risk_score,
            "created_at": scan.created_at.isoformat() if scan.created_at else None,
            "result": result
        })
    
    output = io.BytesIO(json.dumps(data, indent=2).encode())
    
    return send_file(
        output,
        mimetype='application/json',
        as_attachment=True,
        download_name=f'scans_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    )


@report_bp.route("/export/findings/<format>", methods=["GET"])
@jwt_required()
def export_findings(format):
    """Export findings/vulnerabilities in various formats"""
    try:
        user_id = int(get_jwt_identity())
        format = format.lower()
        severity_filter = request.args.get("severity")  # Optional filter
        
        if format not in ["csv", "json"]:
            return jsonify({
                "success": False,
                "error": "Invalid format. Use 'csv' or 'json'"
            }), 400
        
        # Get all findings from user's scans
        scans = Scan.query.filter_by(user_id=user_id).all()
        
        all_findings = []
        for scan in scans:
            result = scan.result or {}
            data = result.get("data", {})
            findings = data.get("findings", [])
            
            for finding in findings:
                if severity_filter and finding.get("severity", "").upper() != severity_filter.upper():
                    continue
                    
                finding_data = {
                    "scan_id": scan.id,
                    "target": scan.target,
                    "scan_type": scan.scan_type,
                    "type": finding.get("type"),
                    "severity": finding.get("severity"),
                    "url": finding.get("url"),
                    "evidence": finding.get("evidence"),
                    "confidence": finding.get("confidence"),
                    "category": finding.get("category"),
                    "exploits_available": len(finding.get("exploits_available", []))
                }
                all_findings.append(finding_data)
        
        if format == "csv":
            return _export_findings_csv(all_findings)
        else:
            return _export_findings_json(all_findings)
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def _export_findings_csv(findings):
    """Export findings to CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        'Scan ID', 'Target', 'Scan Type', 'Finding Type', 'Severity',
        'URL', 'Evidence', 'Confidence', 'Category', 'Exploits Available'
    ])
    
    for finding in findings:
        writer.writerow([
            finding["scan_id"],
            finding["target"],
            finding["scan_type"],
            finding["type"],
            finding["severity"],
            finding["url"],
            finding["evidence"],
            finding["confidence"],
            finding["category"],
            finding["exploits_available"]
        ])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'findings_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )


def _export_findings_json(findings):
    """Export findings to JSON"""
    output = io.BytesIO(json.dumps(findings, indent=2).encode())
    
    return send_file(
        output,
        mimetype='application/json',
        as_attachment=True,
        download_name=f'findings_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    )


@report_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_export_stats():
    """Get statistics about user's data for export preview"""
    try:
        user_id = int(get_jwt_identity())
        
        total_scans = Scan.query.filter_by(user_id=user_id).count()
        
        # Count findings by severity
        scans = Scan.query.filter_by(user_id=user_id).all()
        severity_count = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        
        for scan in scans:
            result = scan.result or {}
            data = result.get("data", {})
            findings = data.get("findings", [])
            
            for finding in findings:
                sev = finding.get("severity", "LOW").upper()
                severity_count[sev] = severity_count.get(sev, 0) + 1
        
        return jsonify({
            "success": True,
            "data": {
                "total_scans": total_scans,
                "total_findings": sum(severity_count.values()),
                "findings_by_severity": severity_count,
                "export_formats": ["csv", "json", "pdf"],
                "generated_at": datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500