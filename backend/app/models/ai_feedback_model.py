"""
AI Feedback Model
Stores user corrections for AI predictions to enable adaptive learning.
This feedback data is used to periodically retrain models and improve accuracy.
"""
from app import db
from datetime import datetime


class AIFeedback(db.Model):
    """
    Stores user feedback on AI predictions for adaptive learning.
    
    Each record represents a correction where a security analyst disagrees
    with the AI's prediction and provides the correct label.
    """
    __tablename__ = "ai_feedback"

    # =========================
    # 🆔 IDENTIFIERS
    # =========================
    id = db.Column(db.Integer, primary_key=True)
    
    # Reference to the scan and AI detection event
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id'), nullable=False, index=True)
    ai_detection_event_id = db.Column(
        db.Integer, 
        db.ForeignKey('ai_detection_events.id'), 
        nullable=True, 
        index=True
    )
    
    # =========================
    # 🧠 AI PREDICTION DATA
    # =========================
    # Original AI prediction
    prediction = db.Column(db.String(50), nullable=False)
    prediction_confidence = db.Column(db.Float, default=0.0, nullable=False)
    
    # User's corrected label
    corrected_label = db.Column(db.String(50), nullable=False)
    
    # Type of scan/data
    source_type = db.Column(
        db.String(50), 
        nullable=False,
        comment="network, system, web, or unified"
    )
    
    # Risk levels
    original_risk_level = db.Column(db.String(20), nullable=True)
    corrected_risk_level = db.Column(db.String(20), nullable=True)
    
    # =========================
    # 📊 FEEDBACK METADATA
    # =========================
    # Whether this feedback has been used in training
    used_for_training = db.Column(db.Boolean, default=False, nullable=False, index=True)
    
    # Which model version incorporated this feedback
    model_version = db.Column(db.String(50), nullable=True)
    
    # Timestamp when used for training
    training_timestamp = db.Column(db.DateTime, nullable=True)
    
    # User-provided notes/reasoning
    feedback_notes = db.Column(db.Text, nullable=True)
    
    # Whether the AI was confident but wrong (important for improvement)
    high_confidence_wrong = db.Column(db.Boolean, default=False, nullable=False)
    
    # =========================
    # 👤 OWNERSHIP
    # =========================
    user_id = db.Column(db.Integer, nullable=False, index=True)
    
    # =========================
    # ⏱ TIMESTAMPS
    # =========================
    feedback_timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
    
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # =========================
    # 🔧 HELPER METHODS
    # =========================
    def to_dict(self):
        """Standardized output for API"""
        return {
            "id": self.id,
            "scan_id": self.scan_id,
            "ai_detection_event_id": self.ai_detection_event_id,
            "source_type": self.source_type,
            "prediction": self.prediction,
            "prediction_confidence": self.prediction_confidence,
            "corrected_label": self.corrected_label,
            "original_risk_level": self.original_risk_level,
            "corrected_risk_level": self.corrected_risk_level,
            "used_for_training": self.used_for_training,
            "model_version": self.model_version,
            "training_timestamp": self.training_timestamp.isoformat() if self.training_timestamp else None,
            "feedback_notes": self.feedback_notes,
            "high_confidence_wrong": self.high_confidence_wrong,
            "user_id": self.user_id,
            "feedback_timestamp": self.feedback_timestamp.isoformat() if self.feedback_timestamp else None,
        }
    
    @classmethod
    def get_untrained_feedback(cls, source_type=None, limit=1000):
        """
        Get feedback records that haven't been used for training yet.
        
        Args:
            source_type: Optional filter by scan type
            limit: Maximum number of records to return
        
        Returns:
            List of AIFeedback objects
        """
        query = cls.query.filter_by(used_for_training=False)
        
        if source_type:
            query = query.filter_by(source_type=source_type)
        
        return query.order_by(cls.feedback_timestamp).limit(limit).all()
    
    @classmethod
    def get_feedback_stats(cls, days=30):
        """
        Get statistics on feedback for model improvement analysis.
        
        Returns:
            dict with feedback counts, accuracy metrics, etc.
        """
        from datetime import timedelta
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        total = cls.query.filter(cls.feedback_timestamp >= cutoff).count()
        untrained = cls.query.filter(
            cls.feedback_timestamp >= cutoff,
            cls.used_for_training == False
        ).count()
        high_conf_wrong = cls.query.filter(
            cls.feedback_timestamp >= cutoff,
            cls.high_confidence_wrong == True
        ).count()
        
        # Count by source type
        by_type = {}
        for source in ['network', 'system', 'web']:
            count = cls.query.filter(
                cls.feedback_timestamp >= cutoff,
                cls.source_type == source
            ).count()
            by_type[source] = count
        
        return {
            "total_feedback": total,
            "untrained_feedback": untrained,
            "high_confidence_wrong": high_conf_wrong,
            "by_source_type": by_type,
            "period_days": days
        }
    
    @classmethod
    def mark_as_trained(cls, feedback_ids, model_version):
        """
        Mark a batch of feedback records as having been used for training.
        
        Args:
            feedback_ids: List of feedback record IDs
            model_version: Version string of the newly trained model
        """
        cls.query.filter(cls.id.in_(feedback_ids)).update({
            'used_for_training': True,
            'model_version': model_version,
            'training_timestamp': datetime.utcnow()
        }, synchronize_session=False)
        
        db.session.commit()
