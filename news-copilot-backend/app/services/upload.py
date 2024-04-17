from werkzeug.utils import secure_filename
import os
from uuid import uuid4

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file(file):
    if file and file.filename and allowed_file(file.filename):
        filename = f"{uuid4()}.{secure_filename(file.filename)}"
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        file_url = f"/{UPLOAD_FOLDER}/{filename}"
        return file_url
    else:
        raise ValueError("Invalid file type")


def get_file(path):
    file_path = os.path.join(os.getcwd(), UPLOAD_FOLDER, path)
    if os.path.exists(file_path):
        return file_path
    else:
        raise FileNotFoundError("Requested file is not found")
