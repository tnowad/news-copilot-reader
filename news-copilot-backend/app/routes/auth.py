from enum import _auto_null
from flask import Blueprint, jsonify, request, Flask
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, JWTManager
from datetime import timedelta
from ..models.user import User
from .. import db
from http import HTTPStatus
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
# TODO: jwt settime access_token and refresh_token 
auth_bp.config["JWT_SECRET_KEY"] = "manager_access123"  # Change this!
auth_bp.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
auth_bp.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=356)
jwt = JWTManager(auth_bp)

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
    access_token = create_access_token(identity=email)
    refresh_token = create_refresh_token(identity=email)

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
    confirm_password = data.get("confirmPassword")
    display_name = data.get("displayName")
    accept_terms = data.get("acceptTerms")

    if not email or not password or not display_name or accept_terms is None:
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.UNPROCESSABLE_ENTITY,
                    "message": "Validation failed",
                    "errors": [
                        {
                            "field": "email",
                            "message": "Email is required" if not email else None,
                        },
                        {
                            "field": "password",
                            "message": "Password is required" if not password else None,
                        },
                        {
                            "field": "displayName",
                            "message": (
                                "Display name is required" if not display_name else None
                            ),
                        },
                        {
                            "field": "acceptTerms",
                            "message": (
                                "Terms acceptance is required"
                                if accept_terms is None
                                else None
                            ),
                        },
                    ],
                }
            ),
            HTTPStatus.UNPROCESSABLE_ENTITY,
        )

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.CONFLICT,
                    "message": "Email already exists",
                    "error": "Email already exists",
                }
            ),
            HTTPStatus.CONFLICT,
        )

    # TODO: Hash the password
    new_user = User(email=email, display_name=display_name, password=password)
    new_user = User(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    # TODO: Generate JWT token and include it in the response
    access_token = create_access_token(identity=email)
    refresh_token = create_refresh_token(identity=email)

    return (
        jsonify(
            {
                "statusCode": HTTPStatus.CREATED,
                "message": "User created successfully",
                "data": {
                    "user": {
                        "id": new_user.id,
                        "email": new_user.email,
                        "roles": ["USER"],
                        "avatar": "",
                        "displayName": new_user.display_name,
                    },
                    "token": {
                        "accessToken": access_token,
                        "refreshToken": refresh_token,
                    },
                },
            }
        ),
        HTTPStatus.CREATED,
    )

# TODO: If we are refreshing a token here we have not verified the users password in
# TODO: a while, so mark the newly created access token as not fresh
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity, fresh=False)
    return jsonify(access_token=access_token)


# TODO: Only allow fresh JWTs to access this route with the `fresh=True` arguement.
@auth_bp.route("/protected", methods=["GET"])
@jwt_required(fresh=True)
def protected():
    return jsonify(foo="bar")


if __name__ == "__main__":
    auth_bp.run()
