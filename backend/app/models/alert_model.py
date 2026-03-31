from app import db
from datetime import datetime

class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    anomaly_id = db.Column(db.Integer, db.ForeignKey("anomalies.id"))
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="open")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "anomaly_id": self.anomaly_id,
            "message": self.message,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }