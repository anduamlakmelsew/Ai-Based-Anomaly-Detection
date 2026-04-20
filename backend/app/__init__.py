from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager

# ========================
# GLOBAL EXTENSIONS
# ========================
db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*", async_mode="threading")
jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    # ========================
    # CONFIG
    # ========================
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../instance/ai_baseline.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "supersecretkey"

    # 🔐 JWT CONFIG
    # 🔐 JWT CONFIG (FIXED)
    app.config["SECRET_KEY"] = "ai_baseline_super_secret_key_2026_secure_12345"

    app.config["JWT_SECRET_KEY"] = "ai_baseline_jwt_super_secure_key_2026_very_long_12345"
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600  # 1 hour
    # ========================
    # INIT EXTENSIONS
    # ========================
    db.init_app(app)
    socketio.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

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

    # ========================
    # DATABASE INIT
    # ========================
    with app.app_context():
        from app.models import user_model, scan_model, settings_model
        db.create_all()

        # Optional seed
        try:
            from app.utils.db_seed import seed_database
            seed_database(app)
        except Exception as e:
            print("⚠️ Seed skipped:", e)

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