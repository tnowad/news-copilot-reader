from datetime import datetime
from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)

from app.decorators.authorization import role_required
from app.models.role import RoleEnum
from app.models.user import User
from app.extensions import db

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
                "avatarImage": current_user.avatar_image,
            }
        },
    }

    style_param = request.args.get("style")

    if style_param == "full":
        response_data["data"]["user"]["bio"] = current_user.bio
        response_data["data"]["user"]["birthDate"] = datetime.strftime(
            current_user.birth_date, "%Y-%m-%d"
        )
        response_data["data"]["user"]["phoneNumber"] = current_user.phone_number

    include_params = request.args.getlist("include")

    if "roles" in include_params:
        roles = [str(role.name) for role in current_user.roles]
        response_data["data"]["user"]["roles"] = roles

    return jsonify(response_data), HTTPStatus.OK


@user_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_current_user_profile():
    current_user = User.query.filter_by(email=get_jwt_identity()).first()
    # check is current user exist

    if not current_user:
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.NOT_FOUND,
                    "message": "User not found",
                }
            ),
            HTTPStatus.NOT_FOUND,
        )
    data = request.json

    # Get all fields
    display_name = data.get("displayName")
    # Get email and do nothing because user can't change email
    email = data.get("email")
    avatar_image = data.get("avatarImage")
    # other fields
    # Get password
    password = data.get("password")
    phone_number = data.get("phoneNumber")
    bio = data.get("bio")
    birth_date = data.get("birthDate")

    # Validate
    if password and not current_user.check_password(password):
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.NOT_FOUND,
                    "message": "Password have already",
                }
            ),
            HTTPStatus.BAD_REQUEST,
        )

    # Assign value and save
    if display_name is not None and current_user.display_name != display_name:
        current_user.display_name = display_name
    if email is not None and not current_user.email != email:
        current_user.email = email
    if avatar_image is not None and not current_user.avatar_image != avatar_image:
        current_user.avatar_image = avatar_image
    if password is not None and not current_user.password != password:
        current_user.password = password
    if phone_number is not None and not current_user.phone_number != phone_number:
        current_user.phone_number = phone_number
    if bio is not None and not current_user.bio != bio:
        current_user.bio = bio
    if birth_date is not None and not current_user.birth_day != birth_date:
        current_user.birth_day = datetime.strptime(birth_date, "%Y-%m-%d")

    db.session.commit()

    return (
        jsonify(
            {
                "statusCode": HTTPStatus.OK,
                "message": "Article updated successfully",
                "data": {
                    "user": {
                        "id": current_user.id,
                        "email": current_user.email,
                        "displayName": current_user.display_name,
                        "avatarImage": current_user.avatar_image,
                    }
                },
            }
        ),
        HTTPStatus.OK,
    )
