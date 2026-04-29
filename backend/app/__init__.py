import os
import logging
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flasgger import Swagger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ========================
# GLOBAL EXTENSIONS
# ========================
db = SQLAlchemy()

# SocketIO with threading mode for stability
# Celery temporarily disabled for stability. Can be reintroduced later for async processing.
socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode="threading",
    logger=True,
    engineio_logger=True
)

jwt = JWTManager()
migrate = Migrate()
swagger = Swagger()


def create_app():
    # Initialize logger FIRST - before any try/except blocks that use it
    import logging
    logger = logging.getLogger(__name__)
    
    app = Flask(__name__)

    # ========================
    # CONFIG
    # ========================
    
    # Security: Load secrets from environment variables
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    
    if not app.config["SECRET_KEY"] or not app.config["JWT_SECRET_KEY"]:
        raise ValueError(
            "SECRET_KEY and JWT_SECRET_KEY must be set in environment variables. "
            "Please configure your .env file."
        )
    
    # Database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///../instance/ai_baseline.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # JWT Configuration
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600  # 1 hour
    
    # Debug mode
    app.config["DEBUG"] = os.getenv("DEBUG", "False").lower() == "true"
    # ========================
    # INIT EXTENSIONS
    # ========================
    db.init_app(app)
    socketio.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    # CORS: Restrict to configured origin instead of wildcard
    cors_origin = os.getenv("CORS_ORIGIN", "http://localhost:5173")
    CORS(app, resources={
        r"/api/*": {
            "origins": cors_origin,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        },
        r"/socket.io/*": {
            "origins": cors_origin
        }
    })
    
    # Setup Swagger/OpenAPI documentation
    swagger.init_app(app)
    
    # Setup logging
    from app.utils.logger import setup_logging
    setup_logging(app)

    # ========================
    # CELERY (DISABLED FOR STABILITY)
    # ========================
    # Celery temporarily disabled for stability. Can be reintroduced later for async processing.
    # All scans now run synchronously for improved reliability.

    # ========================
    # REGISTER BLUEPRINTS
    # ========================
    from app.routes.scan_routes import scan_bp
    app.register_blueprint(scan_bp, url_prefix="/api/scan")

    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    from app.routes.user_routes import user_bp
    app.register_blueprint(user_bp)

    from app.routes.audit_routes import audit_bp
    app.register_blueprint(audit_bp, url_prefix="/api/audit")

    from app.routes.alert_routes import alert_bp
    app.register_blueprint(alert_bp)

    from app.routes.dashboard_routes import dashboard_bp
    app.register_blueprint(dashboard_bp)

    from app.routes.model_routes import model_bp
    app.register_blueprint(model_bp)

    from app.routes.report_routes import report_bp
    app.register_blueprint(report_bp)

    from app.routes.ai_model_routes import ai_model_bp
    app.register_blueprint(ai_model_bp)

    from app.routes.settings_routes import settings_bp
    app.register_blueprint(settings_bp)

    from app.routes.ai_feedback_routes import ai_feedback_bp
    app.register_blueprint(ai_feedback_bp)

    # ========================
    # DATABASE INIT (via Flask-Migrate only)
    # ========================
    with app.app_context():
        # Models imported for migration registration only
        from app.models import (
            user_model, scan_model, settings_model, ai_model,
            ai_feedback_model, ai_detection_event_model
        )
        # Database tables managed via: flask db upgrade
        # Do NOT use db.create_all() - use migrations exclusively

        # Optional seed
        try:
            from app.utils.db_seed import seed_database
            seed_database(app)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"Database seed skipped: {e}")

    # ========================
    # REGISTER SOCKET EVENTS
    # ========================
    from app import socket_events

    # ========================
    # HEALTH CHECK
    # ========================
    @app.route("/ping")
    def ping():
        return {"message": "pong"}

    return app