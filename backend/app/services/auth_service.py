from flask_jwt_extended import create_access_token
from app import db
from app.models.user_model import User
from app.utils.password_validator import validate_password_strength, get_password_strength_score


def generate_username_suggestions(username):
    """Generate username suggestions when taken"""
    base_name = username.lower()
    suggestions = []
    
    # Add numbers
    suggestions.append(f"{base_name}123")
    suggestions.append(f"{base_name}2024")
    
    # Add role-based suffixes
    suggestions.append(f"{base_name}_analyst")
    suggestions.append(f"{base_name}_sec")
    suggestions.append(f"{base_name}_pro")
    
    # Add random numbers
    import random
    suggestions.append(f"{base_name}{random.randint(1, 999)}")
    
    # Add underscores
    suggestions.append(f"{base_name}_{random.randint(1, 99)}")
    
    # Return unique suggestions (remove duplicates)
    return list(dict.fromkeys(suggestions).keys())[:5]  # Return first 5 unique suggestions


class AuthService:

    @staticmethod
    def register(data):
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role", "analyst")

        if not username or not email or not password:
            return {"success": False, "message": "Missing required fields"}, 400

        # Validate password strength
        is_valid, errors = validate_password_strength(password)
        if not is_valid:
            return {
                "success": False, 
                "message": "Password does not meet security requirements",
                "errors": errors
            }, 400

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            # Be more specific about what exists
            if existing_user.username == username and existing_user.email == email:
                return {"success": False, "message": "Username and email already exist"}, 400
            elif existing_user.username == username:
                # Generate username suggestions
                suggestions = generate_username_suggestions(username)
                return {
                    "success": False, 
                    "message": "Username already exists. Please choose a different username.",
                    "suggestions": suggestions
                }, 400
            elif existing_user.email == email:
                return {"success": False, "message": "Email already exists. Please use a different email address."}, 400
            else:
                return {"success": False, "message": "User already exists"}, 400

        user = User(
            username=username,
            email=email,
            role=role
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        # Get password strength feedback for user
        strength_info = get_password_strength_score(password)

        return {
            "success": True,
            "message": "User registered successfully",
            "password_strength": {
                "level": strength_info["level"],
                "score": strength_info["score"]
            }
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

    @staticmethod
    def forgot_password(email):
        """Handle forgot password request - generates temporary reset token"""
        if not email:
            return {"success": False, "message": "Email is required"}, 400

        user = User.query.filter_by(email=email).first()
        
        # Always return success to prevent email enumeration attacks
        if not user:
            return {
                "success": True, 
                "message": "If an account exists with this email, password reset instructions have been sent."
            }, 200

        # Generate a secure temporary password
        import secrets
        import string
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*') for _ in range(12))
        
        # Update user's password with the temporary one
        user.set_password(temp_password)
        db.session.commit()

        return {
            "success": True,
            "message": "Password reset successful. Please use your temporary password to login and change it immediately.",
            "temp_password": temp_password,
            "note": "In production, this would be sent via email. For demo: use the temp_password shown above."
        }, 200