"""
Advanced News Generation Routes
Provides comprehensive news completion and generation endpoints
"""

from flask import Blueprint, request, jsonify
from http import HTTPStatus
import logging
from datetime import datetime

# Import the news completion service
try:
    from app.services.generation.news_completion_service import news_completion_service
    SERVICE_AVAILABLE = True
except ImportError as e:
    logging.error(f"Failed to import news completion service: {e}")
    SERVICE_AVAILABLE = False

advanced_generation_bp = Blueprint("advanced_generation", __name__)
logger = logging.getLogger(__name__)


@advanced_generation_bp.route("/complete-article", methods=["POST"])
def complete_article():
    """
    Complete a news article with context-aware generation
    
    Expected payload:
    {
        "content": "Partial article content...",
        "context": "news|sports|technology|politics|business|health",
        "maxTokens": 100,
        "temperature": 0.7,
        "style": "formal|casual|breaking|analysis"
    }
    """
    try:
        if not request.is_json:
            return jsonify({
                "statusCode": HTTPStatus.BAD_REQUEST,
                "message": "Request must be JSON"
            }), HTTPStatus.BAD_REQUEST
        
        data = request.get_json()
        
        # Validate required fields
        content = data.get("content", "").strip()
        if not content:
            return jsonify({
                "statusCode": HTTPStatus.BAD_REQUEST,
                "message": "Content is required"
            }), HTTPStatus.BAD_REQUEST
        
        # Extract parameters
        context = data.get("context", "news").lower()
        max_tokens = min(data.get("maxTokens", 100), 300)  # Cap at 300
        temperature = max(0.1, min(data.get("temperature", 0.7), 1.5))
        style = data.get("style", "formal").lower()
        
        if not SERVICE_AVAILABLE:
            return _fallback_article_completion(content, context, max_tokens)
        
        # Use the completion service
        result = news_completion_service.complete_article(
            content=content,
            max_tokens=max_tokens,
            temperature=temperature,
            context=context
        )
        
        # Generate headline if requested
        generate_headline = data.get("generateHeadline", False)
        headline = None
        if generate_headline:
            headline = news_completion_service.generate_headline(
                result["completed_text"], 
                style=style
            )
        
        response_data = {
            "statusCode": HTTPStatus.OK,
            "message": "Article completed successfully",
            "data": {
                "originalContent": content,
                "completedContent": result["completed_text"],
                "headline": headline,
                "statistics": {
                    "originalLength": result["original_length"],
                    "generatedLength": result["generated_length"],
                    "totalLength": len(result["completed_text"])
                },
                "metadata": {
                    "context": context,
                    "method": result["method"],
                    "temperature": temperature,
                    "maxTokens": max_tokens,
                    "timestamp": result["timestamp"]
                }
            }
        }
        
        return jsonify(response_data), HTTPStatus.OK
        
    except Exception as e:
        logger.error(f"Article completion error: {str(e)}")
        return jsonify({
            "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
            "message": "Article completion failed",
            "error": "Internal server error"
        }), HTTPStatus.INTERNAL_SERVER_ERROR


@advanced_generation_bp.route("/generate-headline", methods=["POST"])
def generate_headline():
    """
    Generate headlines for news articles
    
    Expected payload:
    {
        "content": "Article content...",
        "style": "breaking|update|analysis|exclusive|standard",
        "maxLength": 100
    }
    """
    try:
        if not request.is_json:
            return jsonify({
                "statusCode": HTTPStatus.BAD_REQUEST,
                "message": "Request must be JSON"
            }), HTTPStatus.BAD_REQUEST
        
        data = request.get_json()
        content = data.get("content", "").strip()
        
        if not content:
            return jsonify({
                "statusCode": HTTPStatus.BAD_REQUEST,
                "message": "Content is required"
            }), HTTPStatus.BAD_REQUEST
        
        style = data.get("style", "standard").lower()
        max_length = data.get("maxLength", 100)
        
        if SERVICE_AVAILABLE:
            headline = news_completion_service.generate_headline(content, style)
        else:
            headline = _fallback_headline_generation(content, style)
        
        # Trim headline if too long
        if len(headline) > max_length:
            headline = headline[:max_length-3] + "..."
        
        return jsonify({
            "statusCode": HTTPStatus.OK,
            "message": "Headline generated successfully",
            "data": {
                "headline": headline,
                "style": style,
                "length": len(headline)
            }
        }), HTTPStatus.OK
        
    except Exception as e:
        logger.error(f"Headline generation error: {str(e)}")
        return jsonify({
            "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
            "message": "Headline generation failed"
        }), HTTPStatus.INTERNAL_SERVER_ERROR


@advanced_generation_bp.route("/continue-story", methods=["POST"])
def continue_story():
    """
    Continue a news story with coherent narrative flow
    
    Expected payload:
    {
        "previousParagraphs": ["Para 1", "Para 2"],
        "context": "news",
        "targetLength": "short|medium|long",
        "tone": "neutral|urgent|analytical"
    }
    """
    try:
        if not request.is_json:
            return jsonify({
                "statusCode": HTTPStatus.BAD_REQUEST,
                "message": "Request must be JSON"
            }), HTTPStatus.BAD_REQUEST
        
        data = request.get_json()
        previous_paragraphs = data.get("previousParagraphs", [])
        
        if not previous_paragraphs:
            return jsonify({
                "statusCode": HTTPStatus.BAD_REQUEST,
                "message": "Previous paragraphs are required"
            }), HTTPStatus.BAD_REQUEST
        
        # Combine paragraphs
        combined_content = " ".join(previous_paragraphs)
        
        context = data.get("context", "news")
        target_length = data.get("targetLength", "medium")
        tone = data.get("tone", "neutral")
        
        # Map target length to token counts
        length_mapping = {"short": 50, "medium": 100, "long": 200}
        max_tokens = length_mapping.get(target_length, 100)
        
        # Adjust temperature based on tone
        tone_temperature = {"neutral": 0.6, "urgent": 0.8, "analytical": 0.5}
        temperature = tone_temperature.get(tone, 0.6)
        
        if SERVICE_AVAILABLE:
            result = news_completion_service.complete_article(
                content=combined_content,
                max_tokens=max_tokens,
                temperature=temperature,
                context=context
            )
            continuation = result["completed_text"][len(combined_content):].strip()
        else:
            continuation = _fallback_story_continuation(combined_content, context, tone)
        
        return jsonify({
            "statusCode": HTTPStatus.OK,
            "message": "Story continued successfully",
            "data": {
                "continuation": continuation,
                "previousContent": combined_content,
                "metadata": {
                    "context": context,
                    "targetLength": target_length,
                    "tone": tone,
                    "actualLength": len(continuation)
                }
            }
        }), HTTPStatus.OK
        
    except Exception as e:
        logger.error(f"Story continuation error: {str(e)}")
        return jsonify({
            "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
            "message": "Story continuation failed"
        }), HTTPStatus.INTERNAL_SERVER_ERROR


@advanced_generation_bp.route("/service-status", methods=["GET"])
def service_status():
    """Get the status of the news generation service"""
    try:
        if SERVICE_AVAILABLE:
            status = news_completion_service.get_service_status()
        else:
            status = {
                "model_loaded": False,
                "fallback_mode": True,
                "service_healthy": True,
                "timestamp": datetime.now().isoformat()
            }
        
        return jsonify({
            "statusCode": HTTPStatus.OK,
            "message": "Service status retrieved",
            "data": status
        }), HTTPStatus.OK
        
    except Exception as e:
        logger.error(f"Service status error: {str(e)}")
        return jsonify({
            "statusCode": HTTPStatus.SERVICE_UNAVAILABLE,
            "message": "Unable to retrieve service status"
        }), HTTPStatus.SERVICE_UNAVAILABLE


# Fallback functions for when the service is not available

def _fallback_article_completion(content: str, context: str, max_tokens: int):
    """Fallback article completion"""
    context_endings = {
        "news": " as authorities continue to investigate and provide updates to the public.",
        "sports": " with fans eagerly awaiting the next match in this exciting season.",
        "technology": " marking another significant milestone in technological advancement.",
        "politics": " as lawmakers work to address concerns raised by constituents.",
        "business": " reflecting ongoing trends in the current economic climate.",
        "health": " according to health officials monitoring the developing situation."
    }
    
    ending = context_endings.get(context, context_endings["news"])
    completed = content + ending
    
    return jsonify({
        "statusCode": HTTPStatus.OK,
        "message": "Article completed (fallback mode)",
        "data": {
            "originalContent": content,
            "completedContent": completed,
            "statistics": {
                "originalLength": len(content),
                "generatedLength": len(ending),
                "totalLength": len(completed)
            },
            "metadata": {
                "context": context,
                "method": "fallback",
                "timestamp": datetime.now().isoformat()
            }
        }
    }), HTTPStatus.OK


def _fallback_headline_generation(content: str, style: str) -> str:
    """Fallback headline generation"""
    first_sentence = content.split('.')[0]
    if len(first_sentence) > 60:
        first_sentence = first_sentence[:60] + "..."
    
    style_prefixes = {
        "breaking": "BREAKING: ",
        "update": "UPDATE: ",
        "analysis": "ANALYSIS: ",
        "exclusive": "EXCLUSIVE: ",
        "standard": ""
    }
    
    return style_prefixes.get(style, "") + first_sentence


def _fallback_story_continuation(content: str, context: str, tone: str) -> str:
    """Fallback story continuation"""
    tone_continuations = {
        "neutral": " The situation continues to develop with officials providing regular updates.",
        "urgent": " Immediate action is being taken to address the rapidly evolving circumstances.",
        "analytical": " Further analysis reveals several key factors contributing to these developments."
    }
    
    return tone_continuations.get(tone, tone_continuations["neutral"])
