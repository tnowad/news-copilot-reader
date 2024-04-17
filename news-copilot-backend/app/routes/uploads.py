from flask import Blueprint, request, jsonify, send_file
from http import HTTPStatus

from app.services.upload import get_file, upload_file

uploads_bp = Blueprint("uploads", __name__)


@uploads_bp.route("/uploads", methods=["POST"])
def upload_file_controller():
    if "file" not in request.files:
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.BAD_REQUEST,
                    "error": "No file part",
                    "message": "No file part provided in the request",
                }
            ),
            HTTPStatus.BAD_REQUEST,
        )

    file = request.files["file"]

    if file.filename == "":
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.BAD_REQUEST,
                    "error": "No selected file",
                    "message": "No file selected for upload",
                }
            ),
            HTTPStatus.BAD_REQUEST,
        )

    try:
        file_url = upload_file(file)
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.OK,
                    "data": {
                        "fileURL": file_url,
                    },
                    "message": "File uploaded successfully",
                }
            ),
            HTTPStatus.OK,
        )
    except ValueError as e:
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.BAD_REQUEST,
                    "error": "Invalid file type",
                    "message": str(e),
                }
            ),
            HTTPStatus.BAD_REQUEST,
        )


@uploads_bp.route("/uploads/<path:path>", methods=["GET"])
def get_file_controller(path):
    try:
        file_path = get_file(path)
        return send_file(file_path)
    except FileNotFoundError as e:
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.NOT_FOUND,
                    "error": "File not found",
                    "message": str(e),
                }
            ),
            HTTPStatus.NOT_FOUND,
        )
