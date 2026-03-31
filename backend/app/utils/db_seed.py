# backend/app/utils/db_seed.py

from app import db   # ✅ ONLY THIS


def seed_database(app):
    from app.models.user_model import User
    from app.models.settings_model import Settings

    # =========================
    # ADMIN USER
    # =========================
    admin = User.query.filter_by(username="admin").first()

    if not admin:
        admin = User(
            username="admin",
            email="admin@test.com",
            role="admin"
        )
        admin.set_password("admin123")
        db.session.add(admin)

    # =========================
    # SETTINGS
    # =========================
    defaults = [
        ("scan_interval", "24h"),
        ("alert_threshold", "0.8"),
        ("report_format", "pdf"),
    ]

    for key, value in defaults:
        if not Settings.query.filter_by(key=key).first():
            db.session.add(Settings(key=key, value=value))

    db.session.commit()

    print("✅ Database seeded successfully")