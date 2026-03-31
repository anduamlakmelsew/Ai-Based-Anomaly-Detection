from app.models.settings_model import Settings
from app import db

def create_setting(key, value):
    setting = Settings(key=key, value=value)
    db.session.add(setting)
    db.session.commit()
    return setting

def get_setting(key):
    return Settings.query.filter_by(key=key).first()

def update_setting(key, value):
    setting = get_setting(key)
    if setting:
        setting.value = value
        db.session.commit()
        return setting
    return None

def list_settings():
    return Settings.query.all()