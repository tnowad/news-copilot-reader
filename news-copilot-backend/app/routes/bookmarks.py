from datetime import datetime
from http import HTTPStatus
import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.models.user import User
from app.services.bookmark_service import BookmarkService
from app.utils.response_helper import APIResponse

logger = logging.getLogger(__name__)
bookmark_service = BookmarkService()

bookmarks_bp = Blueprint("bookmarks", __name__)


def get_current_user_info():
    """Helper function to get current user information"""
    try:
        current_user_email = get_jwt_identity()
        current_user = User.query.filter_by(email=current_user_email).first_or_404()
        return current_user.id, current_user_email
    except Exception as e:
        logger.error(f"Error getting current user info: {str(e)}")
        raise


@bookmarks_bp.route("/bookmarks", methods=["POST"])
@jwt_required()
def create_bookmark():
    """Create a new bookmark"""
    try:
        current_user_id, current_user_email = get_current_user_info()
        data = request.get_json()
        
        if not data:
            return APIResponse.error(
                "Invalid request data",
                status_code=HTTPStatus.BAD_REQUEST
            )
        
        article_id = data.get("articleId")
        user_id = data.get("userId")
        
        if not article_id or not user_id:
            return APIResponse.error(
                "Missing required fields: articleId and userId",
                status_code=HTTPStatus.BAD_REQUEST
            )
        
        logger.info(f"Creating bookmark for article {article_id} by user {current_user_email}")
        
        result = bookmark_service.create_bookmark(article_id, user_id, current_user_id)
        
        if result.get("success"):
            return APIResponse.success(
                result["message"],
                result.get("data"),
                HTTPStatus(result["statusCode"])
            )
        else:
            return APIResponse.error(
                result["message"],
                result.get("error"),
                HTTPStatus(result["statusCode"])
            )
            
    except Exception as e:
        logger.error(f"Error in create_bookmark endpoint: {str(e)}")
        return APIResponse.error(
            "Internal server error",
            str(e),
            HTTPStatus.INTERNAL_SERVER_ERROR
        )


@bookmarks_bp.route("/bookmarks/<int:bookmark_id>", methods=["DELETE"])
@jwt_required()
def delete_bookmark(bookmark_id):
    """Delete a bookmark"""
    try:
        current_user_id, current_user_email = get_current_user_info()
        
        logger.info(f"Deleting bookmark {bookmark_id} by user {current_user_email}")
        
        result = bookmark_service.delete_bookmark(bookmark_id, current_user_id)
        
        if result.get("success"):
            return APIResponse.success(
                result["message"],
                status_code=HTTPStatus(result["statusCode"])
            )
        else:
            return APIResponse.error(
                result["message"],
                result.get("error"),
                HTTPStatus(result["statusCode"])
            )
            
    except Exception as e:
        logger.error(f"Error in delete_bookmark endpoint: {str(e)}")
        return APIResponse.error(
            "Internal server error",
            str(e),
            HTTPStatus.INTERNAL_SERVER_ERROR
        )


@bookmarks_bp.route("/bookmarks", methods=["GET"])
@jwt_required()
def get_bookmarks():
    """Get bookmarks with filtering and pagination"""
    try:
        current_user_id, current_user_email = get_current_user_info()
        
        # Extract query parameters
        filters = {
            'article_id': request.args.get("articleId", type=int),
            'user_id': request.args.get("userId", type=int),
            'limit': request.args.get("limit", type=int) or 10,
            'style': request.args.get("style", type=str) or "compact",
            'includes': request.args.getlist("includes", type=str)
        }
        
        # If no specific user_id provided, use current user
        if not filters['user_id']:
            filters['user_id'] = current_user_id
        
        logger.info(f"Getting bookmarks for user {current_user_email} with filters: {filters}")
        
        result = bookmark_service.get_bookmarks(current_user_id, filters)
        
        if result.get("success"):
            return APIResponse.success(
                result["message"],
                result.get("data"),
                HTTPStatus(result["statusCode"])
            )
        else:
            return APIResponse.error(
                result["message"],
                result.get("error"),
                HTTPStatus(result["statusCode"])
            )
            
    except Exception as e:
        logger.error(f"Error in get_bookmarks endpoint: {str(e)}")
        return APIResponse.error(
            "Internal server error",
            str(e),
            HTTPStatus.INTERNAL_SERVER_ERROR
        )


@bookmarks_bp.route("/bookmarks/<int:bookmark_id>", methods=["GET"])
@jwt_required()
def get_bookmark(bookmark_id):
    """Get a specific bookmark by ID"""
    try:
        current_user_id, current_user_email = get_current_user_info()
        
        logger.info(f"Getting bookmark {bookmark_id} for user {current_user_email}")
        
        result = bookmark_service.get_bookmark_by_id(bookmark_id, current_user_id)
        
        if result.get("success"):
            return APIResponse.success(
                result["message"],
                result.get("data"),
                HTTPStatus(result["statusCode"])
            )
        else:
            return APIResponse.error(
                result["message"],
                result.get("error"),
                HTTPStatus(result["statusCode"])
            )
            
    except Exception as e:
        logger.error(f"Error in get_bookmark endpoint: {str(e)}")
        return APIResponse.error(
            "Internal server error",
            str(e),
            HTTPStatus.INTERNAL_SERVER_ERROR
        )


@bookmarks_bp.route("/bookmarks/check-marked", methods=["POST"])
@jwt_required()
def check_marked():
    """Check which articles are bookmarked by the user"""
    try:
        current_user_id, current_user_email = get_current_user_info()
        data = request.get_json()
        
        if not data:
            return APIResponse.error(
                "Invalid request data",
                status_code=HTTPStatus.BAD_REQUEST
            )
        
        article_ids = data.get("article_ids", [])
        
        if not article_ids or not isinstance(article_ids, list):
            return APIResponse.error(
                "Missing or invalid article_ids",
                status_code=HTTPStatus.BAD_REQUEST
            )
        
        logger.info(f"Checking bookmarked articles for user {current_user_email}")
        
        result = bookmark_service.check_marked_articles(article_ids, current_user_id)
        
        if result.get("success"):
            return APIResponse.success(
                result["message"],
                result.get("data"),
                HTTPStatus(result["statusCode"])
            )
        else:
            return APIResponse.error(
                result["message"],
                result.get("error"),
                HTTPStatus(result["statusCode"])
            )
            
    except Exception as e:
        logger.error(f"Error in check_marked endpoint: {str(e)}")
        return APIResponse.error(
            "Internal server error",
            str(e),
            HTTPStatus.INTERNAL_SERVER_ERROR
        )
