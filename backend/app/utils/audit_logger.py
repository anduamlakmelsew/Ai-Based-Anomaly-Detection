from app.models.log_model import Log
from app import db
from datetime import datetime


def log_action(action, user_id=None, description=None):
    """
    Store an audit log entry.
    """
    log = Log(
        action=action,
        user_id=user_id,
        description=description,
        created_at=datetime.utcnow()
    )

    db.session.add(log)
    db.session.commit()

    return log