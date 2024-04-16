from flask import request, jsonify, Blueprint, send_file
from http import HTTPStatus
from werkzeug.utils import secure_filename
import os
from uuid import uuid4

uploads_bp = Blueprint("uploads", __name__)

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@uploads_bp.route("/uploads", methods=["POST"])
def upload_file():
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

    if file and file.filename and allowed_file(file.filename):
        filename = f"{uuid4()}.{secure_filename(file.filename)}"
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        file_url = f"{request.host_url}{UPLOAD_FOLDER}/{filename}"
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

    return (
        jsonify(
            {
                "statusCode": HTTPStatus.BAD_REQUEST,
                "error": "Invalid file type",
                "message": "Uploaded file type is not supported",
            }
        ),
        HTTPStatus.BAD_REQUEST,
    )


@uploads_bp.route("/uploads/<path:path>", methods=["GET"])
def get_file(path):
    file_path = os.path.join(os.getcwd(), "uploads", path)

    if os.path.exists(file_path):
        return send_file(file_path)

    return (
        jsonify(
            {
                "statusCode": HTTPStatus.NOT_FOUND,
                "error": "File not found",
                "message": "Requested file is not found",
            }
        ),
        HTTPStatus.NOT_FOUND,
    )
