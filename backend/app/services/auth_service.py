from flask_jwt_extended import create_access_token
from app import db
from app.models.user_model import User


class AuthService:

    @staticmethod
    def register(data):
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role", "analyst")

        if not username or not email or not password:
            return {"success": False, "message": "Missing required fields"}, 400

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            return {"success": False, "message": "User already exists"}, 400

        user = User(
            username=username,
            email=email,
            role=role
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return {
            "success": True,
            "message": "User registered successfully"
        }, 201

    @staticmethod
    def login(data):
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return {"success": False, "message": "Email and password required"}, 400

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return {"success": False, "message": "Invalid credentials"}, 401

        access_token = create_access_token(
            identity=str(user.id),   # MUST be string
            additional_claims={"role": user.role}
        )

        return {
            "success": True,
            "data": {
                "token": access_token,
                "user": user.to_dict()
            }
        }, 200