from app.models.log_model import Log
from app import db
from datetime import datetime


def log_action(action, user_id=None, description=None):
    """
    Store an audit log entry.
    """
    # Include description in the action if provided
    action_text = f"{action}: {description}" if description else action
    
    log = Log(
        action=action_text,
        user_id=user_id,
        created_at=datetime.utcnow()
    )

    db.session.add(log)
    db.session.commit()

    return log