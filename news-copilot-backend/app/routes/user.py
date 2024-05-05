from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)
from ..models.user import User
from .. import db
from http import HTTPStatus

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    current_user = User.query.filter_by(email=get_jwt_identity()).first()
    if not current_user:
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.NOT_FOUND,
                    "message": "User not found",
                    "error": "User not found",
                }
            ),
            HTTPStatus.NOT_FOUND,
        )

    print(current_user)

    return (
        jsonify(
            {
                "statusCode": HTTPStatus.OK,
                "message": "User profile",
                "data": {
                    "user": {
                        "id": current_user.id,
                        "email": current_user.email,
                        "displayName": current_user.display_name,
                        "avatar": current_user.avatar,
                    }
                },
            }
        ),
        HTTPStatus.OK,
    )
