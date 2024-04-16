from datetime import datetime
from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)

from app.decorators.authorization import role_required
from app.extensions import db
from app.models.role import RoleEnum
from app.models.user import User

users_bp = Blueprint("user", __name__)


@users_bp.route("/users/profile", methods=["GET"])
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


@users_bp.route("/users", methods=["GET"])
@jwt_required()
def getAllUsers():
    users = User.query.all()
    response_data = {
        "statusCode": HTTPStatus.OK,
        "message": "get all users successful",
        "data": {
            "users": [
                {
                    "id": user.id,
                    "email": user.email,
                    "displayName": user.display_name,
                    "avatarImage": user.avatar_image,
                    "bio": user.bio,
                    "birthDate": datetime.strftime(user.birth_date, "%Y-%m-%d"),
                    "phoneNumber": user.phone_number,
                    "roles": [str(role.name) for role in user.roles],
                    "createdAt": datetime.strftime(user.created_at, "%Y-%m-%d"),
                    "updatedAt": datetime.strftime(user.updated_at, "%Y-%m-%d"),
                }
                for user in users
            ]
        },
    }
    return jsonify(response_data), HTTPStatus.OK


@users_bp.route("/users/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    current_user = User.query.filter_by(id=user_id).first()

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
    data = request.get_json()

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
                    "statusCode": HTTPStatus.BAD_REQUEST,
                    "message": "Password is incorrect",
                }
            ),
            HTTPStatus.BAD_REQUEST,
        )

    # Assign value and save
    if display_name is not None and current_user.display_name != display_name:
        current_user.display_name = display_name
    if avatar_image is not None and current_user.avatar_image != avatar_image:
        current_user.avatar_image = avatar_image
    if phone_number is not None and current_user.phone_number != phone_number:
        current_user.phone_number = phone_number
    if bio is not None and current_user.bio != bio:
        current_user.bio = bio
    if birth_date is not None and current_user.birth_date != birth_date:
        current_user.birth_date = datetime.strptime(birth_date, "%Y-%m-%d")

    response_data = {
        "statusCode": HTTPStatus.OK,
        "message": "User updated successfully",
        "data": {
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "displayName": current_user.display_name,
                "avatarImage": current_user.avatar_image,
                "bio": current_user.bio,
                "birthDate": datetime.strftime(current_user.birth_date, "%Y-%m-%d"),
                "phoneNumber": current_user.phone_number,
                "roles": [str(role.name) for role in current_user.roles],
                "createdAt": datetime.strftime(current_user.created_at, "%Y-%m-%d"),
                "updatedAt": datetime.strftime(current_user.updated_at, "%Y-%m-%d"),
            }
        },
    }

    db.session.commit()

    return (
        jsonify(response_data),
        HTTPStatus.OK,
    )


@users_bp.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    current_user = User.query.filter_by(id=user_id).first()

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

    db.session.delete(current_user)
    db.session.commit()

    response_data = {
        "statusCode": HTTPStatus.OK,
        "message": "User profile deleted successfully",
    }

    return jsonify(response_data), HTTPStatus.OK


@users_bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    display_name = data.get("displayName")
    avatar_image = data.get("avatarImage")
    phone_number = data.get("phoneNumber")
    bio = data.get("bio")
    birth_date = data.get("birthDate")

    if not email:
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.BAD_REQUEST,
                    "message": "Email is required",
                    "error": "Email is required",
                }
            ),
            HTTPStatus.BAD_REQUEST,
        )

    if User.query.filter_by(email=email).first():
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.BAD_REQUEST,
                    "message": "Email is already registered",
                }
            ),
            HTTPStatus.BAD_REQUEST,
        )

    new_user = User(
        email=email,
        password=password,
        display_name=display_name,
        avatar_image=avatar_image,
        phone_number=phone_number,
        bio=bio,
        birth_date=datetime.strptime(birth_date, "%Y-%m-%d"),
    )

    db.session.add(new_user)
    db.session.commit()

    response_data = {
        "statusCode": HTTPStatus.CREATED,
        "message": "User profile created successfully",
        "data": {
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "displayName": new_user.display_name,
                "avatarImage": new_user.avatar_image,
                "bio": new_user.bio,
                "birthDate": new_user.birth_date,
                "phoneNumber": new_user.phone_number,
                "createdAt": datetime.strftime(new_user.created_at, "%Y-%m-%d"),
                "updatedAt": datetime.strftime(new_user.updated_at, "%Y-%m-%d"),
            }
        },
    }

    return jsonify(response_data), HTTPStatus.CREATED


@users_bp.route("/users/profile", methods=["PUT"])
@jwt_required()
def update_profile_user():
    try:
        current_user = User.query.filter_by(email=get_jwt_identity()).first_or_404()
        data = request.get_json()

        display_name = data.get("displayName")
        avatar_image = data.get("avatarImage")
        password = data.get("password")
        phone_number = data.get("phoneNumber")
        bio = data.get("bio")
        birth_date = data.get("birthDate")

        if password and not current_user.check_password(password):
            return (
                jsonify(
                    {
                        "statusCode": HTTPStatus.BAD_REQUEST,
                        "message": "Password is incorrect",
                    }
                ),
                HTTPStatus.BAD_REQUEST,
            )

        if display_name is not None and current_user.display_name != display_name:
            current_user.display_name = display_name
        if (
            avatar_image is not None
            and current_user.avatar_image != avatar_image
            and avatar_image != ""
        ):
            current_user.avatar_image = avatar_image
        if phone_number is not None and current_user.phone_number != phone_number:
            current_user.phone_number = phone_number
        if bio is not None and current_user.bio != bio:
            current_user.bio = bio
        if birth_date is not None and current_user.birth_date != birth_date:
            current_user.birth_date = datetime.strptime(birth_date, "%Y-%m-%d")

        db.session.commit()
        response_data = {
            "statusCode": HTTPStatus.OK,
            "message": "User updated successfully",
            "data": {
                "user": {
                    "id": current_user.id,
                    "email": current_user.email,
                    "displayName": current_user.display_name,
                    "avatarImage": current_user.avatar_image,
                    "bio": current_user.bio,
                    "birthDate": datetime.strftime(current_user.birth_date, "%Y-%m-%d"),
                    "phoneNumber": current_user.phone_number,
                    "roles": [str(role.name) for role in current_user.roles],
                    "createdAt": datetime.strftime(current_user.created_at, "%Y-%m-%d"),
                    "updatedAt": datetime.strftime(current_user.updated_at, "%Y-%m-%d"),
                }
            },
        }

        return (
            jsonify(response_data),
            HTTPStatus.OK,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.BAD_REQUEST,
                    "message": str(e),
                }
            ),
            HTTPStatus.BAD_REQUEST,
        )
