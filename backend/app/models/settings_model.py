from app import db
import json

class Settings(db.Model):
    """
    Key-Value settings storage with JSON support for complex values.
    Supports all scanner, AI, notification, and user preferences.
    """
    __tablename__ = "settings"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=False)  # JSON string for complex values
    value_type = db.Column(db.String(20), default="string")  # string, int, float, bool, json
    category = db.Column(db.String(50), default="general")  # general, scanner, ai, notification, security
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    @classmethod
    def get(cls, key, default=None):
        """Get setting value with automatic type conversion"""
        setting = cls.query.filter_by(key=key).first()
        if not setting:
            return default
        
        if setting.value_type == "json":
            try:
                return json.loads(setting.value)
            except json.JSONDecodeError:
                return default
        elif setting.value_type == "int":
            return int(setting.value)
        elif setting.value_type == "float":
            return float(setting.value)
        elif setting.value_type == "bool":
            return setting.value.lower() in ("true", "1", "yes", "on")
        return setting.value

    @classmethod
    def set(cls, key, value, category="general", description=None):
        """Set setting value with automatic type detection"""
        setting = cls.query.filter_by(key=key).first()
        
        # Determine value type and convert to string
        if isinstance(value, bool):
            value_type = "bool"
            str_value = str(value).lower()
        elif isinstance(value, int):
            value_type = "int"
            str_value = str(value)
        elif isinstance(value, float):
            value_type = "float"
            str_value = str(value)
        elif isinstance(value, (dict, list)):
            value_type = "json"
            str_value = json.dumps(value)
        else:
            value_type = "string"
            str_value = str(value)
        
        if setting:
            setting.value = str_value
            setting.value_type = value_type
            if category:
                setting.category = category
            if description:
                setting.description = description
        else:
            setting = cls(
                key=key,
                value=str_value,
                value_type=value_type,
                category=category,
                description=description
            )
            db.session.add(setting)
        
        db.session.commit()
        return setting

    @classmethod
    def get_all_by_category(cls, category):
        """Get all settings in a category"""
        settings = cls.query.filter_by(category=category).all()
        return {s.key: cls._convert_value(s) for s in settings}

    @classmethod
    def get_all(cls):
        """Get all settings as dict with proper types"""
        settings = cls.query.all()
        result = {}
        for s in settings:
            result[s.key] = cls._convert_value(s)
        return result

    @classmethod
    def _convert_value(cls, setting):
        """Convert stored string value back to proper type"""
        if setting.value_type == "json":
            try:
                return json.loads(setting.value)
            except json.JSONDecodeError:
                return setting.value
        elif setting.value_type == "int":
            return int(setting.value)
        elif setting.value_type == "float":
            return float(setting.value)
        elif setting.value_type == "bool":
            return setting.value.lower() in ("true", "1", "yes", "on")
        return setting.value

    def to_dict(self):
        return {
            "key": self.key,
            "value": self._convert_value(self),
            "type": self.value_type,
            "category": self.category,
            "description": self.description,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }