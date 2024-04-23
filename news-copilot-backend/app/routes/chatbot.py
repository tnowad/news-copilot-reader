from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from getResponseChatBot import getResponseChatBot, predict_class
from app.decorators.authorization import role_required
from app.extensions import db

chatbot_bp = Blueprint("chatbot", __name__)
@chatbot_bp.route('/chatbot', methods=['POST'])
def chatbot_api():
    data = request.get_json()
    message = data['message']
    ints = predict_class(message)
    res = get_response(ints, intents)
    return jsonify({"response": res})