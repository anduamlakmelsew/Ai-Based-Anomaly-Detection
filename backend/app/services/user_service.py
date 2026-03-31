from app.models.users_models import User
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

def create_user(username, password, role="analyst"):
    hashed_pw = generate_password_hash(password)
    user = User(username=username, password=hashed_pw, role=role)
    db.session.add(user)
    db.session.commit()
    return user

def get_user_by_username(username):
    return User.query.filter_by(username=username).first()

def verify_password(user, password):
    return check_password_hash(user.password, password)

def list_users():
    return User.query.all()

def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return True
    return False

def update_user_role(user_id, role):
    user = User.query.get(user_id)
    if user:
        user.role = role
        db.session.commit()
        return user
    return None