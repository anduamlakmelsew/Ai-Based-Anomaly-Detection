from app.models.settings_model import Settings
from app import db
from datetime import datetime

# Default settings configuration
DEFAULT_SETTINGS = {
    # Scanner Settings
    "scan_timeout": {"value": 300, "type": "int", "category": "scanner", "description": "Default scan timeout in seconds"},
    "port_range_start": {"value": 1, "type": "int", "category": "scanner", "description": "Start of port range for network scans"},
    "port_range_end": {"value": 1000, "type": "int", "category": "scanner", "description": "End of port range for network scans"},
    "enable_network_scanner": {"value": True, "type": "bool", "category": "scanner", "description": "Enable network scanner module"},
    "enable_web_scanner": {"value": True, "type": "bool", "category": "scanner", "description": "Enable web vulnerability scanner"},
    "enable_system_scanner": {"value": True, "type": "bool", "category": "scanner", "description": "Enable system audit scanner"},
    "max_concurrent_scans": {"value": 3, "type": "int", "category": "scanner", "description": "Maximum concurrent scans allowed"},
    "scan_interval_minutes": {"value": 60, "type": "int", "category": "scanner", "description": "Default interval between automated scans"},
    
    # AI Model Settings
    "ai_anomaly_threshold": {"value": 0.75, "type": "float", "category": "ai", "description": "AI anomaly detection threshold (0-1)"},
    "enable_ai_analysis": {"value": True, "type": "bool", "category": "ai", "description": "Enable AI analysis for all scans"},
    "enable_ai_network": {"value": True, "type": "bool", "category": "ai", "description": "Enable AI for network scans"},
    "enable_ai_web": {"value": True, "type": "bool", "category": "ai", "description": "Enable AI for web scans"},
    "enable_ai_system": {"value": True, "type": "bool", "category": "ai", "description": "Enable AI for system scans"},
    "active_network_model": {"value": "default", "type": "string", "category": "ai", "description": "Active AI model for network scanning"},
    "active_web_model": {"value": "default", "type": "string", "category": "ai", "description": "Active AI model for web scanning"},
    "active_system_model": {"value": "default", "type": "string", "category": "ai", "description": "Active AI model for system scanning"},
    
    # Notification Settings
    "email_notifications": {"value": True, "type": "bool", "category": "notification", "description": "Enable email notifications"},
    "alert_notifications": {"value": True, "type": "bool", "category": "notification", "description": "Enable alert notifications"},
    "report_notifications": {"value": True, "type": "bool", "category": "notification", "description": "Enable report notifications"},
    "severity_threshold": {"value": "MEDIUM", "type": "string", "category": "notification", "description": "Minimum severity for notifications (LOW, MEDIUM, HIGH, CRITICAL)"},
    "notify_on_critical": {"value": True, "type": "bool", "category": "notification", "description": "Always notify on critical findings"},
    "notify_on_high": {"value": True, "type": "bool", "category": "notification", "description": "Notify on high severity findings"},
    "digest_mode": {"value": False, "type": "bool", "category": "notification", "description": "Send digest emails instead of individual alerts"},
    
    # Security Settings
    "session_timeout": {"value": 60, "type": "int", "category": "security", "description": "Session timeout in minutes"},
    "max_login_attempts": {"value": 5, "type": "int", "category": "security", "description": "Maximum failed login attempts before lockout"},
    "require_strong_password": {"value": True, "type": "bool", "category": "security", "description": "Require strong passwords"},
    "password_min_length": {"value": 8, "type": "int", "category": "security", "description": "Minimum password length"},
    "two_factor_enabled": {"value": False, "type": "bool", "category": "security", "description": "Enable two-factor authentication"},
    "auto_logout": {"value": True, "type": "bool", "category": "security", "description": "Auto logout on inactivity"},
    
    # System Preferences
    "dashboard_refresh_interval": {"value": 30, "type": "int", "category": "system", "description": "Dashboard auto-refresh interval in seconds"},
    "theme": {"value": "dark", "type": "string", "category": "system", "description": "UI theme (light, dark, auto)"},
    "language": {"value": "en", "type": "string", "category": "system", "description": "Interface language"},
    "timezone": {"value": "UTC", "type": "string", "category": "system", "description": "System timezone"},
    "date_format": {"value": "YYYY-MM-DD", "type": "string", "category": "system", "description": "Date display format"},
    "retention_days": {"value": 90, "type": "int", "category": "system", "description": "Data retention period in days"},
    "auto_cleanup": {"value": True, "type": "bool", "category": "system", "description": "Enable automatic data cleanup"},
}


def initialize_default_settings():
    """Initialize all default settings if they don't exist"""
    for key, config in DEFAULT_SETTINGS.items():
        if Settings.get(key) is None:
            Settings.set(
                key=key,
                value=config["value"],
                category=config["category"],
                description=config["description"]
            )
            print(f"Initialized setting: {key}")


def get_setting_value(key, default=None):
    """Get a setting value with proper type conversion"""
    return Settings.get(key, default)


def set_setting_value(key, value, category=None, description=None):
    """Set a setting value"""
    if category is None and key in DEFAULT_SETTINGS:
        category = DEFAULT_SETTINGS[key]["category"]
    if description is None and key in DEFAULT_SETTINGS:
        description = DEFAULT_SETTINGS[key]["description"]
    
    return Settings.set(key, value, category, description)


def get_settings_by_category(category):
    """Get all settings in a category"""
    return Settings.get_all_by_category(category)


def get_all_settings():
    """Get all settings organized by category"""
    all_settings = Settings.get_all()
    
    # Organize by category
    organized = {
        "scanner": {},
        "ai": {},
        "notification": {},
        "security": {},
        "system": {},
        "general": {}
    }
    
    for key, value in all_settings.items():
        setting = Settings.query.filter_by(key=key).first()
        if setting:
            cat = setting.category or "general"
            if cat in organized:
                organized[cat][key] = value
    
    return organized


def update_settings_batch(settings_dict, category=None):
    """Update multiple settings at once"""
    updated = []
    errors = []
    
    for key, value in settings_dict.items():
        try:
            cat = category
            desc = None
            if key in DEFAULT_SETTINGS:
                cat = cat or DEFAULT_SETTINGS[key]["category"]
                desc = DEFAULT_SETTINGS[key]["description"]
            
            Settings.set(key, value, cat, desc)
            updated.append(key)
        except Exception as e:
            errors.append({"key": key, "error": str(e)})
    
    return {"updated": updated, "errors": errors}


def reset_setting_to_default(key):
    """Reset a single setting to its default value"""
    if key in DEFAULT_SETTINGS:
        config = DEFAULT_SETTINGS[key]
        Settings.set(key, config["value"], config["category"], config["description"])
        return True
    return False


def reset_category_to_defaults(category):
    """Reset all settings in a category to defaults"""
    reset_keys = []
    for key, config in DEFAULT_SETTINGS.items():
        if config["category"] == category:
            Settings.set(key, config["value"], category, config["description"])
            reset_keys.append(key)
    return reset_keys


def get_ai_settings():
    """Get AI-related settings"""
    return {
        "anomaly_threshold": get_setting_value("ai_anomaly_threshold", 0.75),
        "enable_ai_analysis": get_setting_value("enable_ai_analysis", True),
        "enable_ai_network": get_setting_value("enable_ai_network", True),
        "enable_ai_web": get_setting_value("enable_ai_web", True),
        "enable_ai_system": get_setting_value("enable_ai_system", True),
        "active_network_model": get_setting_value("active_network_model", "default"),
        "active_web_model": get_setting_value("active_web_model", "default"),
        "active_system_model": get_setting_value("active_system_model", "default"),
    }


def get_scanner_settings():
    """Get scanner configuration"""
    return {
        "timeout": get_setting_value("scan_timeout", 300),
        "port_range_start": get_setting_value("port_range_start", 1),
        "port_range_end": get_setting_value("port_range_end", 1000),
        "enable_network": get_setting_value("enable_network_scanner", True),
        "enable_web": get_setting_value("enable_web_scanner", True),
        "enable_system": get_setting_value("enable_system_scanner", True),
        "max_concurrent": get_setting_value("max_concurrent_scans", 3),
    }


def get_notification_settings():
    """Get notification configuration"""
    return {
        "email_enabled": get_setting_value("email_notifications", True),
        "alert_enabled": get_setting_value("alert_notifications", True),
        "report_enabled": get_setting_value("report_notifications", True),
        "severity_threshold": get_setting_value("severity_threshold", "MEDIUM"),
        "notify_critical": get_setting_value("notify_on_critical", True),
        "notify_high": get_setting_value("notify_on_high", True),
        "digest_mode": get_setting_value("digest_mode", False),
    }


# Legacy compatibility functions
def create_setting(key, value):
    """Legacy: Create a new setting"""
    return Settings.set(key, value)


def get_setting(key):
    """Legacy: Get setting raw object"""
    return Settings.query.filter_by(key=key).first()


def update_setting(key, value):
    """Legacy: Update existing setting"""
    return Settings.set(key, value)


def list_settings():
    """Legacy: List all settings"""
    return Settings.query.all()