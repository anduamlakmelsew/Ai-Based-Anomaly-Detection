from app import db
from datetime import datetime

class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey("scans.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    file_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "scan_id": self.scan_id,
            "user_id": self.user_id,
            "file_path": self.file_path,
            "created_at": self.created_at.isoformat()
        }