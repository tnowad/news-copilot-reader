from flask import Blueprint, jsonify, request
from ..models.user import User
from .. import db
from http import HTTPStatus

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/sign-in", methods=["POST"])
def sign_in():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.UNPROCESSABLE_ENTITY,
                    "message": "Email and password are required",
                    "errors": [
                        {"field": "email", "message": "Email is required"},
                        {"field": "password", "message": "Password is required"},
                    ],
                }
            ),
            HTTPStatus.UNPROCESSABLE_ENTITY,
        )

    user = User.query.filter_by(email=email).first()

    # TODO: Use check_password method
    if not user or not user.password == password:
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.UNAUTHORIZED,
                    "message": "Invalid email or password",
                    "error": "Invalid email or password",
                }
            ),
            HTTPStatus.UNAUTHORIZED,
        )

    # TODO: Generate JWT token and include it in the response
    access_token = "fake-access-token"
    refresh_token = "fake-refresh-token"

    return (
        jsonify(
            {
                "statusCode": HTTPStatus.OK,
                "message": "Login successful",
                "data": {
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "displayName": user.display_name,
                        "avatar": user.avatar,
                        "roles": ["GUEST", "USER", "WRITER", "ADMIN"],
                    },
                    "token": {
                        "accessToken": access_token,
                        "refreshToken": refresh_token,
                    },
                },
            }
        ),
        HTTPStatus.OK,
    )


@auth_bp.route("/sign-up", methods=["POST"])
def sign_up():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already exists"}), 400

    # TODO: Hash the password
    new_user = User(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    # TODO: Generate JWT token and include it in the response

    return jsonify({"message": "User created successfully"}), 201
