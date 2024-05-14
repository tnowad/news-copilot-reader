from datetime import datetime
from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)

from app.decorators.authorization import role_required
from app.extensions import db
from app.models.role import Role, RoleEnum
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
        ) if current_user.birth_date else None
        response_data["data"]["user"]["phoneNumber"] = current_user.phone_number

    include_params = request.args.getlist("include")

    if "roles" in include_params:
        roles = [str(role.name) for role in current_user.roles]
        response_data["data"]["user"]["roles"] = roles

    return jsonify(response_data), HTTPStatus.OK


@users_bp.route("/users", methods=["GET"])
def get_users():
    try:
        page = request.args.get("page", type=int) or 1
        limit = request.args.get("limit", type=int) or 10
        search = request.args.get("search", type=str)
        sort_by = request.args.get("sortBy", type=str)
        sort_order = request.args.get("sortOrder", type=str)

        query = User.query

        if search:
            query = query.filter(User.display_name.ilike(f"%{search}%"))

        if sort_by:
            if sort_by == "display_name":
                query = query.order_by(User.display_name)

        if sort_order:
            if sort_order == "desc":
                query = query.order_by(User.display_name.desc())
            elif sort_order == "asc":
                query = query.order_by(User.display_name.asc())

        total_users = query.count()

        if page and limit:
            offset = (page - 1) * limit
            query = query.offset(offset).limit(limit)

        users = query.all()

        users_data = []
        for user in users:
            user_info = {
                "id": user.id,
                "email": user.email,
                "displayName": user.display_name,
                "avatarImage": user.avatar_image,
                "bio": user.bio,
                # "birthDate": datetime.strftime(user.birth_date, "%Y-%m-%d"),
                "phoneNumber": user.phone_number,
                "roles": [str(role.name) for role in user.roles],
                # "createdAt": datetime.strftime(user.created_at, "%Y-%m-%d"),
                # "updatedAt": datetime.strftime(user.updated_at, "%Y-%m-%d"),
            }
            users_data.append(user_info)

        metadata = {
            "pagination": {
                "offset": (page - 1) * limit if (page and limit) else None,
                "limit": limit,
                "previousOffset": (page - 2) * limit if page > 1 else None,
                "nextOffset": page * limit if len(users) == limit else None,
                "currentPage": page if page else None,
                "pageCount": (
                    (total_users + limit - 1) // limit if page and limit else None
                ),
                "totalCount": total_users,
            },
            "sortedBy": {"name": sort_by, "order": sort_order},
            "filters": {
                "search": search,
            },
        }

        response_data = {
            "statusCode": HTTPStatus.OK,
            "message": "Get all users route",
            "data": {"users": users_data, "metadata": metadata},
        }

        return jsonify(response_data), HTTPStatus.OK

    except Exception as e:
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
                    "message": "Internal Server Error",
                    "error": str(e),
                }
            ),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


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

    display_name = data.get("displayName")
    avatar_image = data.get("avatarImage")
    password = data.get("password")
    phone_number = data.get("phoneNumber")
    bio = data.get("bio")
    birth_date = data.get("birthDate")
    roleIds = data.get_list("roleIds")

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
    if avatar_image is not None and current_user.avatar_image != avatar_image:
        current_user.avatar_image = avatar_image
    if phone_number is not None and current_user.phone_number != phone_number:
        current_user.phone_number = phone_number
    if bio is not None and current_user.bio != bio:
        current_user.bio = bio
    if birth_date is not None and current_user.birth_date != birth_date:
        current_user.birth_date = datetime.strptime(birth_date, "%Y-%m-%d")

    if roleIds:
        current_user.roles.clear()
        for roleId in roleIds:
            role = Role.query.filter_by(id=roleId).first()
            if role:
                current_user.roles.append(role)

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


@users_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    if user_id is None:
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.BAD_REQUEST,
                    "message": "User ID is required",
                }
            ),
            HTTPStatus.BAD_REQUEST,
        )

    user = User.query.get(user_id)

    if not user:
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
                "id": user.id,
                "email": user.email,
                "displayName": user.display_name,
                "avatarImage": user.avatar_image,
            }
        },
    }

    style_param = request.args.get("style")

    if style_param == "full":
        response_data["data"]["user"]["bio"] = user.bio
        response_data["data"]["user"]["birthDate"] = datetime.strftime(
            user.birth_date, "%Y-%m-%d"
        )
        response_data["data"]["user"]["phoneNumber"] = user.phone_number

    include_params = request.args.getlist("include")

    if "roles" in include_params:
        roles = [str(role.name) for role in user.roles]
        response_data["data"]["user"]["roles"] = roles

    return jsonify(response_data), HTTPStatus.OK


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
