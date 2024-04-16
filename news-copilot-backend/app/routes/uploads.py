from flask import request, jsonify, Blueprint, send_from_directory
from http import HTTPStatus
from werkzeug.utils import secure_filename
import os

uploads_bp = Blueprint("uploads", __name__)

UPLOAD_FOLDER = "static/uploads/"

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
                }
            ),
            HTTPStatus.BAD_REQUEST,
        )

    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        file_url = f"{request.host_url}{UPLOAD_FOLDER}/{filename}"
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.OK,
                    "data": {
                        "fileURL": file_url,
                    },
                }
            ),
            HTTPStatus.OK,
        )

    return (
        jsonify(
            {
                "statusCode": HTTPStatus.BAD_REQUEST,
                "error": "Invalid file type",
            }
        ),
        HTTPStatus.BAD_REQUEST,
    )
