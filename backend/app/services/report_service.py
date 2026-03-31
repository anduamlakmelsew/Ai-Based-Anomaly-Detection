from app.models.report_model import Report
from app import db
from datetime import datetime

def create_report(title, content, user_id=None):
    report = Report(title=title, content=content, user_id=user_id, created_at=datetime.utcnow())
    db.session.add(report)
    db.session.commit()
    return report

def list_reports():
    return Report.query.order_by(Report.created_at.desc()).all()

def get_report(report_id):
    return Report.query.get(report_id)

def delete_report(report_id):
    report = Report.query.get(report_id)
    if report:
        db.session.delete(report)
        db.session.commit()
        return True
    return False