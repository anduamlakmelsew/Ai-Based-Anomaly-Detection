from app.models.alert_model import Alert
from app import db
from datetime import datetime

def create_alert(message, severity, anomaly_id=None):
    alert = Alert(message=message, severity=severity, anomaly_id=anomaly_id, created_at=datetime.utcnow())
    db.session.add(alert)
    db.session.commit()
    return alert

def list_alerts():
    return Alert.query.order_by(Alert.created_at.desc()).all()

def get_alert(alert_id):
    return Alert.query.get(alert_id)

def delete_alert(alert_id):
    alert = Alert.query.get(alert_id)
    if alert:
        db.session.delete(alert)
        db.session.commit()
        return True
    return False