from http import HTTPStatus

from flask import Blueprint, jsonify, request

chatbot_bp = Blueprint("chatbot", __name__)


@chatbot_bp.route("/chat", methods=["POST"])
def chatbot_api():
    try:
        from app.services.chatbot.chatbot import (
            getResponseChatBot,
            predict_class,
            intents,
        )

        data = request.get_json()
        message = data["message"]

        ints = predict_class(message)

        res = getResponseChatBot(ints, intents)
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
