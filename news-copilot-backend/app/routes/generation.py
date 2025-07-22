from flask import Blueprint, request, jsonify
from app.extensions import cache
from http import HTTPStatus
import logging

generation_bp = Blueprint("generation", __name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@cache.memoize(timeout=300)
def generate_text_cached(prompt, max_length=100, temperature=0.7, top_k=20, top_p=0.9):
    """Cached text generation for improved performance"""
    try:
        from app.services.generation.text_generation import text_generation_pipeline
        
        # Generate text using the custom transformer
        result = text_generation_pipeline(
            prompt=prompt,
            max_length=max_length,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p
        )
        
        if result and len(result) > 0:
            return result[0].get("generated_text", prompt)
        else:
            return prompt + " [Generation failed - using original prompt]"
            
    except Exception as e:
        logger.error(f"Text generation error: {str(e)}")
        return prompt + " [Generation service temporarily unavailable]"


@generation_bp.route("/generate-text", methods=["POST"])
def generate_text():
    """
    Generate text completion for news articles
    
    Expected JSON payload:
    {
        "prompt": "Breaking news: New AI breakthrough",
        "maxLength": 100,
        "temperature": 0.7,
        "topK": 20,
        "topP": 0.9
    }
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                "statusCode": HTTPStatus.BAD_REQUEST,
                "message": "Request must be JSON",
                "error": "Invalid content type"
            }), HTTPStatus.BAD_REQUEST
        
        data = request.get_json()
        
        # Extract parameters with defaults
        prompt = data.get("prompt", "").strip()
        max_length = min(data.get("maxLength", 50), 200)  # Cap at 200 tokens
        temperature = max(0.1, min(data.get("temperature", 0.7), 2.0))  # Clamp between 0.1-2.0
        top_k = max(1, min(data.get("topK", 20), 100))  # Clamp between 1-100
        top_p = max(0.1, min(data.get("topP", 0.9), 1.0))  # Clamp between 0.1-1.0
        
        # Validate prompt
        if not prompt:
            return jsonify({
                "statusCode": HTTPStatus.BAD_REQUEST,
                "message": "Prompt is required",
                "error": "Empty prompt provided"
            }), HTTPStatus.BAD_REQUEST
        
        if len(prompt) > 1000:
            return jsonify({
                "statusCode": HTTPStatus.BAD_REQUEST,
                "message": "Prompt too long",
                "error": "Prompt must be less than 1000 characters"
            }), HTTPStatus.BAD_REQUEST
        
        logger.info(f"Generating text for prompt length: {len(prompt)}, max_length: {max_length}")
        
        # Generate text
        generated_text = generate_text_cached(
            prompt=prompt,
            max_length=max_length,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p
        )
        
        # Prepare response
        response_data = {
            "statusCode": HTTPStatus.OK,
            "message": "Text generated successfully",
            "data": {
                "generatedText": generated_text,
                "prompt": prompt,
                "parameters": {
                    "maxLength": max_length,
                    "temperature": temperature,
                    "topK": top_k,
                    "topP": top_p
                }
            },
        }

        return jsonify(response_data), HTTPStatus.OK

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            "statusCode": HTTPStatus.BAD_REQUEST,
            "message": "Invalid parameters",
            "error": str(e)
        }), HTTPStatus.BAD_REQUEST
        
    except Exception as e:
        logger.error(f"Generation service error: {str(e)}")
        return jsonify({
            "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
            "message": "Text generation failed",
            "error": "Internal server error occurred"
        }), HTTPStatus.INTERNAL_SERVER_ERROR


@generation_bp.route("/generate-completion", methods=["POST"])
def generate_completion():
    """
    Generate news article completion with smart context handling
    
    Expected JSON payload:
    {
        "content": "Partial article content...",
        "context": "news|sports|technology|politics|etc",
        "length": "short|medium|long"
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
        context = data.get("context", "news").lower()
        length = data.get("length", "medium").lower()
        
        if not content:
            return jsonify({
                "statusCode": HTTPStatus.BAD_REQUEST,
                "message": "Content is required"
            }), HTTPStatus.BAD_REQUEST
        
        # Map length to token counts
        length_mapping = {
            "short": 30,
            "medium": 80,
            "long": 150
        }
        max_tokens = length_mapping.get(length, 80)
        
        # Adjust temperature based on context
        context_temp = {
            "news": 0.6,
            "sports": 0.7,
            "technology": 0.8,
            "politics": 0.5,
            "entertainment": 0.9,
            "business": 0.6
        }
        temperature = context_temp.get(context, 0.7)
        
        # Generate completion
        generated_text = generate_text_cached(
            prompt=content,
            max_length=max_tokens,
            temperature=temperature,
            top_k=25,
            top_p=0.85
        )
        
        return jsonify({
            "statusCode": HTTPStatus.OK,
            "message": "Article completion generated",
            "data": {
                "originalContent": content,
                "completedContent": generated_text,
                "context": context,
                "length": length
            }
        }), HTTPStatus.OK
        
    except Exception as e:
        logger.error(f"Article completion error: {str(e)}")
        return jsonify({
            "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
            "message": "Article completion failed",
            "error": str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR


@generation_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for the generation service"""
    try:
        from app.services.generation.text_generation import news_generator
        
        model_status = "available" if hasattr(news_generator, 'generator') and news_generator.generator else "fallback"
        
        return jsonify({
            "statusCode": HTTPStatus.OK,
            "message": "Generation service is healthy",
            "data": {
                "modelStatus": model_status,
                "cacheEnabled": cache is not None,
                "timestamp": str(int(__import__('time').time()))
            }
        }), HTTPStatus.OK
        
    except Exception as e:
        return jsonify({
            "statusCode": HTTPStatus.SERVICE_UNAVAILABLE,
            "message": "Generation service health check failed",
            "error": str(e)
        }), HTTPStatus.SERVICE_UNAVAILABLE
