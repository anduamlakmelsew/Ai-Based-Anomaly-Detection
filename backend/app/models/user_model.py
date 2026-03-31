from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user")

    # =========================
    # 🔐 SET PASSWORD
    # =========================
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # =========================
    # 🔍 CHECK PASSWORD
    # =========================
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)