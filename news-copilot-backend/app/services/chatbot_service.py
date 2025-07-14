from typing import Dict, Any, Optional
from http import HTTPStatus
import logging

from app.services.base_service import BaseService
from app.extensions import cache

logger = logging.getLogger(__name__)


class ChatbotService(BaseService):
    """Service for managing chatbot interactions"""
    
    def __init__(self):
        super().__init__(None)  # No specific model class for chatbot
    
    def process_chat_message(self, message: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Process a chat message and return bot response"""
        try:
            if not message or not message.strip():
                logger.warning("Empty message received")
                return self._format_error_response(
                    HTTPStatus.BAD_REQUEST,
                    "Message is required",
                    "Empty or invalid message provided"
                )

            # Sanitize message
            message = message.strip()
            
            # Build cache key for response caching
            cache_key = f"chatbot_response:{hash(message.lower())}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info(f"Returning cached chatbot response for message: {message[:50]}...")
                return cached_result

            # Import chatbot components (lazy loading)
            try:
                from app.services.chatbot.chatbot import (
                    getResponseChatBot,
                    predict_class,
                    intents,
                )
            except ImportError as e:
                logger.error(f"Failed to import chatbot components: {str(e)}")
                return self._format_error_response(
                    HTTPStatus.SERVICE_UNAVAILABLE,
                    "Chatbot service unavailable",
                    "Chatbot system is not available"
                )

            # Process message through chatbot
            try:
                # Predict intent class
                predicted_intents = predict_class(message)
                
                if not predicted_intents:
                    logger.warning(f"No intents predicted for message: {message}")
                    return self._format_response(
                        HTTPStatus.OK,
                        "No suitable response found",
                        {
                            "response": "I'm sorry, I don't understand that. Could you please rephrase your question?",
                            "confidence": 0.0,
                            "intent": "unknown"
                        }
                    )

                # Get response from chatbot
                bot_response = getResponseChatBot(predicted_intents, intents)
                
                if not bot_response:
                    logger.warning(f"Empty response from chatbot for message: {message}")
                    bot_response = "I'm sorry, I couldn't process your request right now. Please try again."

                # Extract confidence and intent if available
                confidence = predicted_intents[0].get('probability', 0.0) if predicted_intents else 0.0
                intent = predicted_intents[0].get('intent', 'unknown') if predicted_intents else 'unknown'

                result = self._format_response(
                    HTTPStatus.OK,
                    "Chat response generated successfully",
                    {
                        "response": bot_response,
                        "confidence": confidence,
                        "intent": intent,
                        "message_id": self._generate_message_id()
                    }
                )

                # Cache the result for 1 hour (chatbot responses can be cached longer)
                cache.set(cache_key, result, timeout=3600)

                logger.info(f"Generated chatbot response for intent '{intent}' with confidence {confidence}")
                return result

            except Exception as e:
                logger.error(f"Error processing message through chatbot: {str(e)}")
                return self._format_error_response(
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    "Failed to process chat message",
                    str(e)
                )

        except Exception as e:
            logger.error(f"Error in chatbot service: {str(e)}")
            return self._format_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Chatbot service error",
                str(e)
            )

    def get_chatbot_health(self) -> Dict[str, Any]:
        """Health check for chatbot service"""
        try:
            # Check if chatbot components are available
            try:
                from app.services.chatbot.chatbot import (
                    getResponseChatBot,
                    predict_class,
                    intents,
                )
                chatbot_available = True
                chatbot_error = None
                
                # Test basic functionality
                test_intents = predict_class("hello")
                test_response = getResponseChatBot(test_intents, intents) if test_intents else None
                
            except ImportError as e:
                chatbot_available = False
                chatbot_error = f"Import error: {str(e)}"
                test_response = None
            except Exception as e:
                chatbot_available = False
                chatbot_error = f"Runtime error: {str(e)}"
                test_response = None

            # Check cache availability
            try:
                cache.get("health_check")
                cache_available = True
                cache_error = None
            except Exception as e:
                cache_available = False
                cache_error = str(e)

            # Check intents availability
            try:
                intents_available = bool(intents) if chatbot_available else False
                intents_count = len(intents) if intents_available else 0
            except:
                intents_available = False
                intents_count = 0

            # Determine overall health
            overall_healthy = chatbot_available and cache_available and intents_available

            health_data = {
                "service": "chatbot",
                "status": "healthy" if overall_healthy else "unhealthy",
                "timestamp": self._get_current_timestamp(),
                "components": {
                    "chatbot_engine": {
                        "status": "available" if chatbot_available else "unavailable",
                        "error": chatbot_error
                    },
                    "cache": {
                        "status": "available" if cache_available else "unavailable",
                        "error": cache_error
                    },
                    "intents": {
                        "status": "available" if intents_available else "unavailable",
                        "count": intents_count
                    }
                },
                "features": {
                    "chat_processing": "enabled" if chatbot_available else "disabled",
                    "response_caching": "enabled" if cache_available else "disabled",
                    "intent_recognition": "enabled" if intents_available else "disabled"
                },
                "test_results": {
                    "basic_functionality": "passed" if test_response else "failed",
                    "response_sample": test_response[:100] if test_response else None
                }
            }

            status_code = HTTPStatus.OK if overall_healthy else HTTPStatus.SERVICE_UNAVAILABLE

            return self._format_response(
                status_code,
                "Chatbot service health check completed",
                health_data
            )

        except Exception as e:
            logger.error(f"Error in chatbot health check: {str(e)}")
            return self._format_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Health check failed",
                str(e)
            )

    def get_conversation_history(self, user_id: int, limit: int = 10) -> Dict[str, Any]:
        """Get conversation history for a user (placeholder for future implementation)"""
        try:
            # This is a placeholder for future conversation history functionality
            # Currently, the chatbot doesn't store conversation history
            
            logger.info(f"Conversation history requested for user {user_id}")
            
            return self._format_response(
                HTTPStatus.OK,
                "Conversation history retrieved",
                {
                    "conversations": [],
                    "total": 0,
                    "note": "Conversation history feature is not yet implemented"
                }
            )

        except Exception as e:
            logger.error(f"Error retrieving conversation history: {str(e)}")
            return self._format_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Failed to retrieve conversation history",
                str(e)
            )

    def _generate_message_id(self) -> str:
        """Generate a unique message ID"""
        import uuid
        return str(uuid.uuid4())

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

    def _serialize(self, data: Any) -> Dict[str, Any]:
        """Basic serialization for chatbot responses"""
        return {
            "response": str(data),
            "timestamp": self._get_current_timestamp()
        }
