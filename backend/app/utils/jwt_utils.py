from flask_jwt_extended import create_access_token
from datetime import timedelta


def generate_token(user):
    """
    Generate JWT token for a user
    """

    token = create_access_token(
        identity=user.id,
        additional_claims={
            "role": user.role,
            "username": user.username
        },
        expires_delta=timedelta(hours=8)
    )

    return token