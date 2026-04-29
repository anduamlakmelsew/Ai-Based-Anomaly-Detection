# app/routes/dashboard_routes.py
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from app.models.scan_model import Scan
from app.models.alert_model import Alert
from app.models.anomaly_model import Anomaly
from app import db

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_dashboard_stats():
    """
    Get comprehensive dashboard statistics with real-time data
    """
    try:
        user_id = int(get_jwt_identity())
        
        # Time ranges
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        last_30d = now - timedelta(days=30)
        
        # Get user's scans
        user_scans = Scan.query.filter_by(user_id=user_id)
        
        # Total scans
        total_scans = user_scans.count()
        scans_24h = user_scans.filter(Scan.created_at >= last_24h).count()
        scans_7d = user_scans.filter(Scan.created_at >= last_7d).count()
        scans_30d = user_scans.filter(Scan.created_at >= last_30d).count()
        
        # Get all scans for detailed analysis
        recent_scans = user_scans.order_by(Scan.created_at.desc()).limit(50).all()
        
        # Calculate findings by severity
        severity_count = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
        total_findings = 0
        exploitable_count = 0
        
        # AI anomaly detection stats
        ai_predictions = {"normal": 0, "anomaly": 0, "error": 0}
        avg_confidence = 0
        confidence_sum = 0
        confidence_count = 0
        
        # Scan type distribution
        scan_types = {"network": 0, "web": 0, "system": 0}
        
        # Risk scores over time for trends
        risk_scores = []
        
        for scan in recent_scans:
            result = scan.result or {}
            data = result.get("data", {})
            findings = data.get("findings", [])
            
            # Count scan types
            scan_type = scan.scan_type.lower() if scan.scan_type else "unknown"
            if scan_type in scan_types:
                scan_types[scan_type] += 1
            
            # Risk scores for trend analysis
            risk_score = data.get("risk_analysis", {}).get("total_risk_score", 0)
            if risk_score:
                risk_scores.append({
                    "date": scan.created_at.isoformat(),
                    "score": risk_score
                })
            
            # Process findings
            for finding in findings:
                severity = finding.get("severity", "LOW").upper()
                severity_count[severity] = severity_count.get(severity, 0) + 1
                total_findings += 1
                
                if finding.get("exploits_available", []):
                    exploitable_count += 1
            
            # AI analysis results
            ai_result = result.get("ai_analysis", {})
            prediction = ai_result.get("prediction", "unknown")
            confidence = ai_result.get("confidence", 0)
            
            if prediction in ai_predictions:
                ai_predictions[prediction] += 1
            
            if confidence > 0:
                confidence_sum += confidence
                confidence_count += 1
        
        avg_confidence = round(confidence_sum / confidence_count, 3) if confidence_count > 0 else 0
        
        # Calculate current risk level
        latest_scan = user_scans.order_by(Scan.created_at.desc()).first()
        current_risk = {"score": 0, "level": "LOW", "trend": "stable"}
        
        if latest_scan:
            result = latest_scan.result or {}
            data = result.get("data", {})
            risk_analysis = data.get("risk_analysis", {})
            current_risk = {
                "score": risk_analysis.get("total_risk_score", 0),
                "level": risk_analysis.get("risk_level", "LOW"),
                "trend": "stable"  # TODO: Calculate from risk_scores trend
            }
        
        # Get recent alerts count
        recent_alerts = Alert.query.filter(
            Alert.created_at >= last_24h
        ).count() if hasattr(Alert, 'created_at') else 0
        
        # Get recent anomalies detected by AI
        recent_anomalies = Anomaly.query.filter_by(
            user_id=user_id
        ).filter(
            Anomaly.detected_at >= last_7d
        ).count() if hasattr(Anomaly, 'detected_at') else ai_predictions.get("anomaly", 0)
        
        return jsonify({
            "success": True,
            "data": {
                "scans": {
                    "total": total_scans,
                    "last_24h": scans_24h,
                    "last_7d": scans_7d,
                    "last_30d": scans_30d,
                    "by_type": scan_types
                },
                "findings": {
                    "total": total_findings,
                    "by_severity": severity_count,
                    "exploitable": exploitable_count,
                    "critical_rate": round(severity_count["CRITICAL"] / total_findings * 100, 2) if total_findings > 0 else 0
                },
                "risk": current_risk,
                "ai_insights": {
                    "predictions": ai_predictions,
                    "avg_confidence": avg_confidence,
                    "anomalies_detected_7d": recent_anomalies,
                    "model_coverage": {
                        "network": True,
                        "web": True,
                        "system": True
                    }
                },
                "alerts": {
                    "total_unacknowledged": recent_alerts,
                    "last_24h": recent_alerts
                },
                "trends": {
                    "risk_scores": risk_scores[:20]  # Last 20 scans
                },
                "generated_at": now.isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@dashboard_bp.route("/summary", methods=["GET"])
@jwt_required()
def summary():
    """
    Quick summary for dashboard header
    """
    try:
        user_id = int(get_jwt_identity())
        
        total_scans = Scan.query.filter_by(user_id=user_id).count()
        
        # Get findings count from recent scans
        recent_scans = Scan.query.filter_by(user_id=user_id).order_by(
            Scan.created_at.desc()
        ).limit(10).all()
        
        total_findings = 0
        for scan in recent_scans:
            result = scan.result or {}
            data = result.get("data", {})
            total_findings += len(data.get("findings", []))
        
        # Count anomalies from AI results
        anomaly_count = 0
        for scan in recent_scans:
            result = scan.result or {}
            ai = result.get("ai_analysis", {})
            if ai.get("prediction") == "anomaly":
                anomaly_count += 1
        
        return jsonify({
            "success": True,
            "data": {
                "scans": total_scans,
                "findings": total_findings,
                "anomalies": anomaly_count,
                "risk_score": recent_scans[0].risk_score if recent_scans else 0
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@dashboard_bp.route("/activity", methods=["GET"])
@jwt_required()
def get_activity_feed():
    """
    Get recent activity for dashboard activity log
    """
    try:
        user_id = int(get_jwt_identity())
        limit = min(int(request.args.get("limit", 20)), 100)
        
        # Get recent scans as activity
        recent_scans = Scan.query.filter_by(user_id=user_id).order_by(
            Scan.created_at.desc()
        ).limit(limit).all()
        
        activities = []
        for scan in recent_scans:
            result = scan.result or {}
            data = result.get("data", {})
            findings = data.get("findings", [])
            
            activities.append({
                "id": scan.id,
                "type": "scan",
                "scan_type": scan.scan_type,
                "target": scan.target,
                "status": scan.status,
                "timestamp": scan.created_at.isoformat(),
                "findings_count": len(findings),
                "risk_score": scan.risk_score,
                "ai_prediction": result.get("ai_analysis", {}).get("prediction", "unknown"),
                "severity_breakdown": {
                    "CRITICAL": sum(1 for f in findings if f.get("severity") == "CRITICAL"),
                    "HIGH": sum(1 for f in findings if f.get("severity") == "HIGH"),
                    "MEDIUM": sum(1 for f in findings if f.get("severity") == "MEDIUM"),
                    "LOW": sum(1 for f in findings if f.get("severity") == "LOW")
                }
            })
        
        return jsonify({
            "success": True,
            "data": activities
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@dashboard_bp.route("/ai-insights", methods=["GET"])
@jwt_required()
def get_ai_insights():
    """
    Get AI-powered insights and recommendations
    """
    try:
        user_id = int(get_jwt_identity())
        
        # Get recent scans for analysis
        recent_scans = Scan.query.filter_by(user_id=user_id).order_by(
            Scan.created_at.desc()
        ).limit(30).all()
        
        if not recent_scans:
            return jsonify({
                "success": True,
                "data": {
                    "insights": [],
                    "recommendations": ["Start scanning to get AI-powered insights"],
                    "risk_trend": "insufficient_data"
                }
            })
        
        insights = []
        recommendations = []
        
        # Analyze risk trend
        risk_scores = []
        for scan in recent_scans:
            if scan.risk_score is not None:
                risk_scores.append(scan.risk_score)
        
        if risk_scores:
            avg_risk = sum(risk_scores) / len(risk_scores)
            max_risk = max(risk_scores)
            
            if avg_risk > 50:
                insights.append({
                    "type": "risk",
                    "level": "high",
                    "message": f"Average risk score is {avg_risk:.1f} - attention needed"
                })
                recommendations.append("Review high-risk findings and prioritize remediation")
            
            if max_risk > 80:
                insights.append({
                    "type": "risk",
                    "level": "critical",
                    "message": f"Maximum risk score of {max_risk} detected"
                })
                recommendations.append("Immediate action required for critical risk items")
        
        # Analyze AI predictions
        anomaly_count = 0
        for scan in recent_scans:
            result = scan.result or {}
            ai = result.get("ai_analysis", {})
            if ai.get("prediction") == "anomaly":
                anomaly_count += 1
        
        if anomaly_count > 0:
            insights.append({
                "type": "anomaly",
                "level": "warning",
                "message": f"AI detected {anomaly_count} potential anomalies in recent scans"
            })
            recommendations.append("Review AI-flagged anomalies for potential security issues")
        
        # Scan frequency recommendation
        if len(recent_scans) < 5:
            recommendations.append("Increase scan frequency for better security visibility")
        
        # Check for stale scans
        latest_scan = recent_scans[0]
        days_since_scan = (datetime.utcnow() - latest_scan.created_at).days
        if days_since_scan > 7:
            recommendations.append(f"Last scan was {days_since_scan} days ago - schedule a new scan")
        
        return jsonify({
            "success": True,
            "data": {
                "insights": insights,
                "recommendations": recommendations,
                "risk_trend": "improving" if len(risk_scores) > 1 and risk_scores[0] < risk_scores[-1] else "stable",
                "last_updated": datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500