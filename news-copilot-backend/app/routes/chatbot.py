from http import HTTPStatus
import http

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.services.chatbot.chatbot import getResponseChatBot, predict_class, intents
from app.decorators.authorization import role_required
from app.extensions import db

chatbot_bp = Blueprint("chatbot", __name__)


@chatbot_bp.route("/chatbot", methods=["POST"])
def chatbot_api():
    try:
        data = request.get_json()
        message = data["message"]

        # Dự đoán lớp cho tin nhắn
        ints = predict_class(message)

        # Nhận câu trả lời từ dự đoán và dữ liệu đào tạo
        res = getResponseChatBot(ints, intents)
        # Trả về phản hồi thành công
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.OK,
                    "message": "answer success",
                    "response": res,
                }
            ),
            HTTPStatus.OK,
        )
    except Exception as e:
        # Trả về phản hồi lỗi nếu có lỗi xảy ra
        error_message = "Internal Server Error: " + str(e)
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
                    "message": "error answer",
                    "error": error_message,
                }
            ),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
