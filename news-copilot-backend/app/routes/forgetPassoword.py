from flask import Blueprint, request, jsonify
from app.extensions import cache, mail
import random
import string
from http import HTTPStatus
from flask_mail import Message

forgotPassword_bp = Blueprint("forgotPassword", __name__)


def generate_random_code():
    return "".join(random.choices(string.digits, k=6))


@forgotPassword_bp.route("/forgot_password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    email = data.get("email")

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

    # Generate random 6-digit code
    code = generate_random_code()

    # Store code in cache with 1 hour expiry
    cache.set(email, code, timeout=3600)

    # Send email with the code
    send_reset_email(email, code)

    return jsonify({"message": "Password reset code sent successfully"}), 200


def send_reset_email(email, code):
    # Send email with the code
    msg = Message("Password Reset Code", recipients=[email])
    msg.body = f"Your password reset code is: {code}"
    mail.send(msg)
