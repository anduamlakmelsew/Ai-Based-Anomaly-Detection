"""
AI Detection Event Model
Stores AI analysis results for security monitoring
"""
from app import db
from datetime import datetime


class AIDetectionEvent(db.Model):
    """
    Stores every AI detection event from network, system, and web analysis.
    Provides historical data for dashboard and SOC-style monitoring.
    """
    __tablename__ = "ai_detection_events"

    # =========================
    # 🆔 IDENTIFIERS
    # =========================
    id = db.Column(db.Integer, primary_key=True)
    
    # Reference to original scan if applicable
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id'), nullable=True, index=True)
    
    # =========================
    # 📡 SOURCE INFORMATION
    # =========================
    source_type = db.Column(
        db.String(50), 
        nullable=False, 
        index=True,
        comment="network, system, web, or unified"
    )
    target = db.Column(db.String(255), nullable=False, index=True)
    
    # =========================
    # 🧠 AI PREDICTION RESULTS
    # =========================
    # Risk assessment
    risk_level = db.Column(
        db.String(20), 
        nullable=False, 
        index=True,
        comment="LOW, MEDIUM, HIGH, CRITICAL"
    )
    risk_score = db.Column(db.Float, default=0.0, nullable=False)
    global_status = db.Column(db.String(20), nullable=True)
    
    # Attack/Anomaly details
    attack_type = db.Column(db.String(100), nullable=True, index=True)
    attack_category = db.Column(db.String(100), nullable=True)
    vulnerability_type = db.Column(db.String(100), nullable=True)
    
    # Confidence scores
    confidence = db.Column(db.Float, default=0.0, nullable=False)
    attack_probability = db.Column(db.Float, nullable=True)
    anomaly_score = db.Column(db.Float, nullable=True)
    
    # =========================
    # 📊 DETAILED RESULTS (JSON)
    # =========================
    # Complete AI prediction results
    network_prediction = db.Column(db.JSON, default=dict, nullable=True)
    system_prediction = db.Column(db.JSON, default=dict, nullable=True)
    web_prediction = db.Column(db.JSON, default=dict, nullable=True)
    
    # Full unified result
    unified_result = db.Column(db.JSON, default=dict, nullable=True)
    
    # Raw input data (sanitized)
    input_data = db.Column(db.JSON, default=dict, nullable=True)
    
    # =========================
    # ⚙️ MODEL METADATA
    # =========================
    model_status = db.Column(db.String(20), default="ok", nullable=False)
    degraded_mode = db.Column(db.Boolean, default=False, nullable=False)
    missing_inputs = db.Column(db.JSON, default=dict, nullable=True)
    
    # =========================
    # 👤 OWNERSHIP
    # =========================
    user_id = db.Column(db.Integer, nullable=False, index=True)
    
    # =========================
    # ⏱ TIMESTAMPS
    # =========================
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
    
    # =========================
    # 🔧 HELPER METHODS
    # =========================
    def to_dict(self):
        """
        Standardized output for API / dashboard
        """
        return {
            "id": self.id,
            "scan_id": self.scan_id,
            "source_type": self.source_type,
            "target": self.target,
            "risk": {
                "level": self.risk_level,
                "score": self.risk_score,
                "global_status": self.global_status
            },
            "detection": {
                "attack_type": self.attack_type,
                "attack_category": self.attack_category,
                "vulnerability_type": self.vulnerability_type,
                "confidence": self.confidence
            },
            "model": {
                "status": self.model_status,
                "degraded_mode": self.degraded_mode,
                "missing_inputs": self.missing_inputs
            },
            "predictions": {
                "network": self.network_prediction,
                "system": self.system_prediction,
                "web": self.web_prediction,
                "unified": self.unified_result
            },
            "timestamp": self.created_at.isoformat() if self.created_at else None
        }
    
    def to_dashboard_format(self):
        """
        Simplified format for dashboard display
        """
        return {
            "id": self.id,
            "source": self.source_type,
            "target": self.target,
            "risk_level": self.risk_level,
            "risk_score": round(self.risk_score, 1),
            "attack_type": self.attack_type or self.attack_category or self.vulnerability_type or "Unknown",
            "confidence": round(self.confidence, 2),
            "timestamp": self.created_at.isoformat() if self.created_at else None,
            "status": "CRITICAL" if self.risk_level == "CRITICAL" else 
                     "HIGH" if self.risk_level == "HIGH" else
                     "MEDIUM" if self.risk_level == "MEDIUM" else "LOW"
        }
    
    @classmethod
    def get_recent_events(cls, limit=100, user_id=None, source_type=None):
        """
        Get recent AI detection events
        """
        query = cls.query
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        if source_type:
            query = query.filter_by(source_type=source_type)
        
        return query.order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_critical_events(cls, limit=50, user_id=None):
        """
        Get critical and high risk events
        """
        query = cls.query.filter(
            cls.risk_level.in_(["CRITICAL", "HIGH"])
        )
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        return query.order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_risk_stats(cls, hours=24, user_id=None):
        """
        Get risk statistics for the dashboard
        """
        from datetime import timedelta
        
        since = datetime.utcnow() - timedelta(hours=hours)
        query = cls.query.filter(cls.created_at >= since)
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        events = query.all()
        
        stats = {
            "total": len(events),
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "by_source": {
                "network": 0,
                "system": 0,
                "web": 0,
                "unified": 0
            }
        }
        
        for event in events:
            level = event.risk_level.lower()
            if level in stats:
                stats[level] += 1
            
            source = event.source_type.lower()
            if source in stats["by_source"]:
                stats["by_source"][source] += 1
        
        return stats


# Update models/__init__.py to include this model
# from .ai_detection_event_model import AIDetectionEvent
