from functools import wraps
from http import HTTPStatus
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models.user import User


def role_required(roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user_email = get_jwt_identity()
            user = User.query.filter_by(email=current_user_email).first()

            if user and any(
                role in [str(role.name) for role in user.roles] for role in roles
            ):
                return func(*args, **kwargs)
            else:
                return (
                    jsonify(
                        {
                            "statusCode": HTTPStatus.FORBIDDEN,
                            "message": "Insufficient privileges",
                            "error": "Roles required: {}".format(", ".join(roles)),
                        }
                    ),
                    HTTPStatus.FORBIDDEN,
                )

        return wrapper

    return decorator
