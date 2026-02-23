from flask import Flask
from flask_jwt_extended import JWTManager
from .database import db

def create_app():
    app = Flask(__name__)

    #  Configuration
    app.config["SECRET_KEY"] = "super-secret-key-change-this"
    app.config["JWT_SECRET_KEY"] = "jwt-secret-string-change-this"

    #  PostgreSQL Configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:Yitayh2334@localhost:5432/ai_scanner"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize Extensions
    db.init_app(app)
    JWTManager(app)

    # Register Blueprints (we will implement routes later)
    from app.auth.routes import auth_bp
    from app.scanner.routes import scanner_bp
    from app.baseline.routes import baseline_bp
    from app.reports.routes import reports_bp
    from app.alerts.routes import alerts_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(scanner_bp, url_prefix="/api")
    app.register_blueprint(baseline_bp, url_prefix="/api")
    app.register_blueprint(reports_bp, url_prefix="/api")
    app.register_blueprint(alerts_bp, url_prefix="/api")

    return app