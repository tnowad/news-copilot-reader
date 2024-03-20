from functools import wraps
from http import HTTPStatus
from typing import List

from flask import jsonify
from flask_jwt_extended import get_jwt_identity

from app.models.role import RoleEnum
from app.models.user import User


def role_required(roles: List[RoleEnum]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user_email = get_jwt_identity()
            user: User | None = User.query.filter_by(email=current_user_email).first()

            if user and any(
                str(role.value) in [str(user_role.name) for user_role in user.roles]
                for role in roles
            ):
                return func(*args, **kwargs)
            else:
                return (
                    jsonify(
                        {
                            "statusCode": HTTPStatus.FORBIDDEN,
                            "message": "Insufficient privileges",
                            "error": "Roles required: {}".format(
                                ", ".join([role.value for role in roles])
                            ),
                        }
                    ),
                    HTTPStatus.FORBIDDEN,
                )

        return wrapper

    return decorator
