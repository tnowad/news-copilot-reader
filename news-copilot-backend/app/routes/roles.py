from http import HTTPStatus
from flask import Blueprint, jsonify, request
from app.models.article import Article
from app.models.role import Role

roles_bp = Blueprint("roles", __name__)


@roles_bp.route("/roles", methods=["GET"])
def get_roles():
    try:
        roles = Role.query.all()

        response_data = {
            "statusCode": HTTPStatus.OK,
            "message": "Get all roles",
            "data": {
                "roles": [
                    {
                        "id": role.id,
                        "name": str(role.name),
                    }
                    for role in roles
                ]
            },
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
