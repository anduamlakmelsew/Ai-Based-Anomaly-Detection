"""
AI Feedback Routes
API endpoints for submitting and managing AI prediction feedback
"""
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.ai_feedback_model import AIFeedback
from app.models.ai_detection_event_model import AIDetectionEvent
from app.models.scan_model import Scan
from app import db
from app.utils.audit_logger import log_action

logger = logging.getLogger(__name__)

ai_feedback_bp = Blueprint("ai_feedback", __name__, url_prefix="/api/ai")


@ai_feedback_bp.route("/feedback", methods=["POST"])
@jwt_required()
def submit_feedback():
    """
    Submit feedback on an AI prediction.
    
    Security analysts use this to correct AI predictions,
    creating training data for model improvement.
    
    Request body:
    {
        "scan_id": 123,
        "ai_detection_event_id": 456,  # optional
        "prediction": "safe",
        "corrected_label": "vulnerable",
        "original_risk_level": "LOW",
        "corrected_risk_level": "HIGH",
        "feedback_notes": "AI missed SQL injection vulnerability",
        "source_type": "web"
    }
    
    Returns:
        Success confirmation with feedback record ID
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["scan_id", "prediction", "corrected_label", "source_type"]
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400
        
        scan_id = data.get("scan_id")
        
        # Verify scan exists and belongs to user
        scan = Scan.query.filter_by(id=scan_id, user_id=user_id).first()
        if not scan:
            return jsonify({
                "success": False,
                "error": "Scan not found or access denied"
            }), 404
        
        # Get AI detection event if provided
        ai_event_id = data.get("ai_detection_event_id")
        ai_event = None
        if ai_event_id:
            ai_event = AIDetectionEvent.query.filter_by(
                id=ai_event_id, 
                scan_id=scan_id,
                user_id=user_id
            ).first()
            if not ai_event:
                logger.warning(f"AI detection event {ai_event_id} not found for scan {scan_id}")
        
        # Determine if AI was confident but wrong
        prediction_confidence = data.get("prediction_confidence", 0.0)
        high_confidence_wrong = prediction_confidence > 0.8 and data["prediction"] != data["corrected_label"]
        
        # Create feedback record
        feedback = AIFeedback(
            scan_id=scan_id,
            ai_detection_event_id=ai_event_id,
            source_type=data.get("source_type"),
            prediction=data.get("prediction"),
            prediction_confidence=prediction_confidence,
            corrected_label=data.get("corrected_label"),
            original_risk_level=data.get("original_risk_level"),
            corrected_risk_level=data.get("corrected_risk_level"),
            feedback_notes=data.get("feedback_notes"),
            high_confidence_wrong=high_confidence_wrong,
            user_id=user_id,
            used_for_training=False
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        # Audit log
        log_action(
            action="ai_feedback_submitted",
            user_id=user_id,
            description=f"Feedback submitted for scan {scan_id}: '{data['prediction']}' corrected to '{data['corrected_label']}'"
        )
        
        logger.info(f"AI feedback submitted: id={feedback.id}, scan={scan_id}, user={user_id}")
        
        return jsonify({
            "success": True,
            "message": "Feedback submitted successfully",
            "feedback_id": feedback.id,
            "high_confidence_correction": high_confidence_wrong
        }), 201
        
    except Exception as e:
        logger.exception("Failed to submit AI feedback")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@ai_feedback_bp.route("/feedback/stats", methods=["GET"])
@jwt_required()
def get_feedback_stats():
    """
    Get statistics on AI feedback for dashboard display.
    
    Query params:
        days: Number of days to include (default 30)
    
    Returns:
        Feedback counts, training status, etc.
    """
    try:
        user_id = int(get_jwt_identity())
        days = request.args.get('days', 30, type=int)
        
        # Get overall stats
        stats = AIFeedback.get_feedback_stats(days=days)
        
        # Get user's personal stats
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        user_feedback_count = AIFeedback.query.filter(
            AIFeedback.user_id == user_id,
            AIFeedback.feedback_timestamp >= cutoff
        ).count()
        
        return jsonify({
            "success": True,
            "data": {
                "overall": stats,
                "user_contributions": user_feedback_count,
                "period_days": days
            }
        })
        
    except Exception as e:
        logger.exception("Failed to get feedback stats")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@ai_feedback_bp.route("/feedback/history", methods=["GET"])
@jwt_required()
def get_feedback_history():
    """
    Get user's feedback history.
    
    Query params:
        limit: Number of records (default 50, max 100)
        source_type: Filter by type (network, system, web)
    
    Returns:
        List of feedback records
    """
    try:
        user_id = int(get_jwt_identity())
        limit = min(request.args.get('limit', 50, type=int), 100)
        source_type = request.args.get('source_type')
        
        query = AIFeedback.query.filter_by(user_id=user_id)
        
        if source_type:
            query = query.filter_by(source_type=source_type)
        
        feedback_list = query.order_by(
            AIFeedback.feedback_timestamp.desc()
        ).limit(limit).all()
        
        return jsonify({
            "success": True,
            "data": [f.to_dict() for f in feedback_list],
            "count": len(feedback_list)
        })
        
    except Exception as e:
        logger.exception("Failed to get feedback history")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@ai_feedback_bp.route("/feedback/<int:feedback_id>", methods=["DELETE"])
@jwt_required()
def delete_feedback(feedback_id):
    """
    Delete a feedback record (only by the user who created it).
    """
    try:
        user_id = int(get_jwt_identity())
        
        feedback = AIFeedback.query.filter_by(
            id=feedback_id,
            user_id=user_id
        ).first()
        
        if not feedback:
            return jsonify({
                "success": False,
                "error": "Feedback not found or access denied"
            }), 404
        
        # Don't allow deleting feedback that's been used for training
        if feedback.used_for_training:
            return jsonify({
                "success": False,
                "error": "Cannot delete feedback that has been used for model training"
            }), 400
        
        db.session.delete(feedback)
        db.session.commit()
        
        logger.info(f"AI feedback {feedback_id} deleted by user {user_id}")
        
        return jsonify({
            "success": True,
            "message": "Feedback deleted"
        })
        
    except Exception as e:
        logger.exception("Failed to delete feedback")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
