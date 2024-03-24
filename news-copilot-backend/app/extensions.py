from http import HTTPStatus

from flask import jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()
jwt = JWTManager()


@jwt.unauthorized_loader
def unauthorized_response(callback):
    return (
        jsonify(
            {
                "statusCode": HTTPStatus.UNAUTHORIZED,
                "message": "Unauthorized",
                "error": "Missing Authorization Header",
            }
        ),
        HTTPStatus.UNAUTHORIZED,
    )


@jwt.expired_token_loader
def expired_token_response(callback):
    return (
        jsonify(
            {
                "statusCode": HTTPStatus.UNAUTHORIZED,
                "message": "Unauthorized",
                "error": "Token has expired",
            }
        ),
        HTTPStatus.UNAUTHORIZED,
    )


@jwt.invalid_token_loader
def invalid_token_response(callback):
    return (
        jsonify(
            {
                "statusCode": HTTPStatus.UNAUTHORIZED,
                "message": "Unauthorized",
                "error": "Invalid token",
            }
        ),
        HTTPStatus.UNAUTHORIZED,
    )
