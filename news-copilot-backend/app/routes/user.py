from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)

from app.decorators.authorization import role_required
from app.models.role import RoleEnum
from app.models.user import User

user_bp = Blueprint("user", __name__, url_prefix="/users")


@user_bp.route("/profile", methods=["GET"])
@jwt_required()
@role_required([RoleEnum.USER, RoleEnum.ADMIN, RoleEnum.WRITER])
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

    response_data = {
        "statusCode": HTTPStatus.OK,
        "message": "User profile",
        "data": {
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "displayName": current_user.display_name,
            }
        },
    }

    include_params = request.args.getlist("include")

    if "roles" in include_params:
        roles = [str(role.name) for role in current_user.roles]
        response_data["data"]["user"]["roles"] = roles

    if "avatarImage" in include_params:
        response_data["data"]["user"]["avatarImage"] = current_user.avatar_image

    return jsonify(response_data), HTTPStatus.OK
