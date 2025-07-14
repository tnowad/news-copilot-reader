from http import HTTPStatus
import logging

from flask import Blueprint, request

from app.services.recommendation_service import RecommendationService
from app.utils.response_helper import APIResponse

logger = logging.getLogger(__name__)
recommendation_service = RecommendationService()

recommendations_bp = Blueprint("recommendations", __name__)


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


@recommendations_bp.route("/recommendations/articles", methods=["GET"])
def get_recommendations_articles():
    """Get article recommendations using hybrid recommender"""
    try:
        # Extract and validate query parameters
        user_id = request.args.get("userId", type=int)
        article_id = request.args.get("articleId", type=int)
        limit = request.args.get("limit", type=int) or 10
        style = request.args.get("style", type=str) or "compact"
        includes = request.args.getlist("includes", type=str)

        logger.info(f"Getting article recommendations for user {user_id}, article {article_id}")
        
        result = recommendation_service.get_recommended_articles(
            user_id=user_id,
            article_id=article_id,
            limit=limit,
            style=style,
            includes=includes
        )
        
        return handle_service_response(
            result,
            "Recommendations retrieved successfully",
            "Failed to retrieve recommendations"
        )
        
    except Exception as e:
        logger.error(f"Error in get_recommendations_articles endpoint: {str(e)}")
        return APIResponse.error(
            "Internal server error",
            str(e),
            HTTPStatus.INTERNAL_SERVER_ERROR
        )


@recommendations_bp.route("/recommendations/health", methods=["GET"])
def recommendations_health_check():
    """Health check endpoint for recommendations service"""
    try:
        logger.info("Performing recommendations service health check")
        
        result = recommendation_service.get_recommendation_health()
        
        return handle_service_response(
            result,
            "Recommendations service health check completed",
            "Recommendations service health check failed"
        )
        
    except Exception as e:
        logger.error(f"Error in recommendations health check endpoint: {str(e)}")
        return APIResponse.error(
            "Health check failed",
            str(e),
            HTTPStatus.SERVICE_UNAVAILABLE
        )
