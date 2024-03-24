from http import HTTPStatus
from flask import Blueprint, jsonify

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return (
        jsonify(
            {
                "statusCode": HTTPStatus.OK,
                "message": "Welcome to News Copilot Reader API, please refer to the documentation for more information.",
                "data": {
                    "project": "News Copilot Reader API",
                    "authors": [
                        "Nguyen Minh Tuan",
                        "Nguyen Duc Huy",
                        "Ta Vinh Quang",
                        "Nguyen Manh Duc",
                    ],
                },
            }
        ),
        HTTPStatus.OK,
    )
