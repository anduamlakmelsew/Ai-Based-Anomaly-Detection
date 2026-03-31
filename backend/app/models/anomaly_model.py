from app import db
from datetime import datetime

class Anomaly(db.Model):
    __tablename__ = "anomalies"

    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey("scans.id"))
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), default="low")
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "scan_id": self.scan_id,
            "description": self.description,
            "severity": self.severity,
            "detected_at": self.detected_at.isoformat()
        }