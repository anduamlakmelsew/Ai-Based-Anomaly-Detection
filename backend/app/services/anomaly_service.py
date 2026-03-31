from app.models.anomaly_model import Anomaly
from app import db
from datetime import datetime

def create_anomaly(description, severity, scan_id=None):
    anomaly = Anomaly(description=description, severity=severity, scan_id=scan_id, created_at=datetime.utcnow())
    db.session.add(anomaly)
    db.session.commit()
    return anomaly

def list_anomalies():
    return Anomaly.query.order_by(Anomaly.created_at.desc()).all()

def get_anomaly(anomaly_id):
    return Anomaly.query.get(anomaly_id)

def delete_anomaly(anomaly_id):
    anomaly = Anomaly.query.get(anomaly_id)
    if anomaly:
        db.session.delete(anomaly)
        db.session.commit()
        return True
    return False