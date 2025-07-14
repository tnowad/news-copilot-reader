from http import HTTPStatus
import logging

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.user import User
from app.services.chatbot_service import ChatbotService
from app.utils.response_helper import APIResponse

logger = logging.getLogger(__name__)
chatbot_service = ChatbotService()

logger = logging.getLogger(__name__)
chatbot_service = ChatbotService()

chatbot_bp = Blueprint("chatbot", __name__)


def get_current_user_info():
    """Helper function to get current user information"""
    try:
        current_user_email = get_jwt_identity()
        if current_user_email:
            current_user = User.query.filter_by(email=current_user_email).first()
            return current_user.id if current_user else None, current_user_email
        return None, None
    except Exception as e:
        logger.error(f"Error getting current user info: {str(e)}")
        return None, None


def handle_service_response(result, success_message, error_message, success_status=HTTPStatus.OK):
    """Helper function to handle service responses consistently"""
    if result.get("success"):
        return APIResponse.success(
            message=success_message,
            data=result.get("data"),
            status_code=HTTPStatus(result["statusCode"])
        )
    else:
        return APIResponse.error(
            message=error_message,
            error_details=result.get("message"),
            status_code=HTTPStatus(result["statusCode"])
        )


@chatbot_bp.route("/chat", methods=["POST"])
def chatbot_api():
    """Process chat message and return bot response"""
    try:
        user_id, user_email = get_current_user_info()
        data = request.get_json()

        if not data:
            return APIResponse.error(
                "Invalid request data",
                status_code=HTTPStatus.BAD_REQUEST
            )

        message = data.get("message")
        if not message:
            return APIResponse.error(
                "Message is required",
                status_code=HTTPStatus.BAD_REQUEST
            )

        logger.info(f"Processing chat message from user {user_email or 'anonymous'}")
        
        result = chatbot_service.process_chat_message(message, user_id)
        
        return handle_service_response(
            result,
            "Chat response generated successfully",
            "Failed to process chat message"
        )
        
    except Exception as e:
        logger.error(f"Error in chatbot_api endpoint: {str(e)}")
        return APIResponse.error(
            "Internal server error",
            str(e),
            HTTPStatus.INTERNAL_SERVER_ERROR
        )


@chatbot_bp.route("/chat/health", methods=["GET"])
def chatbot_health_check():
    """Health check endpoint for chatbot service"""
    try:
        logger.info("Performing chatbot service health check")
        
        result = chatbot_service.get_chatbot_health()
        
        return handle_service_response(
            result,
            "Chatbot service health check completed",
            "Chatbot service health check failed"
        )
        
    except Exception as e:
        logger.error(f"Error in chatbot health check endpoint: {str(e)}")
        return APIResponse.error(
            "Health check failed",
            str(e),
            HTTPStatus.SERVICE_UNAVAILABLE
        )


@chatbot_bp.route("/chat/history", methods=["GET"])
@jwt_required()
def get_conversation_history():
    """Get conversation history for the current user"""
    try:
        user_id, user_email = get_current_user_info()
        
        if not user_id:
            return APIResponse.error(
                "User authentication required",
                status_code=HTTPStatus.UNAUTHORIZED
            )

        limit = request.args.get("limit", type=int) or 10
        
        logger.info(f"Getting conversation history for user {user_email}")
        
        result = chatbot_service.get_conversation_history(user_id, limit)
        
        return handle_service_response(
            result,
            "Conversation history retrieved successfully",
            "Failed to retrieve conversation history"
        )
        
    except Exception as e:
        logger.error(f"Error in get_conversation_history endpoint: {str(e)}")
        return APIResponse.error(
            "Internal server error",
            str(e),
            HTTPStatus.INTERNAL_SERVER_ERROR
        )
