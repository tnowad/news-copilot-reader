from datetime import datetime
from http import HTTPStatus
import logging

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.models.user import User
from app.services.comment_service import CommentService
from app.utils.response_helper import APIResponse

logger = logging.getLogger(__name__)
comment_service = CommentService()

comments_bp = Blueprint("comments", __name__)


def get_current_user_info():
    """Helper function to get current user information"""
    try:
        current_user_email = get_jwt_identity()
        current_user = User.query.filter_by(email=current_user_email).first_or_404()
        return current_user.id, current_user_email
    except Exception as e:
        logger.error(f"Error getting current user info: {str(e)}")
        raise


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


@comments_bp.route("/comments", methods=["GET"])
def get_comments():
    """Get comments with filtering and pagination"""
    try:
        # Extract and validate query parameters
        filters = {
            'page': request.args.get("page", type=int) or 1,
            'limit': request.args.get("limit", type=int) or 10,
            'sort_by': request.args.get("sortBy", type=str),
            'sort_order': request.args.get("sortOrder", type=str),
            'style': request.args.get("style", type=str),
            'includes': request.args.getlist("includes", type=str),
            'user_id': request.args.get("userId", type=int),
            'article_id': request.args.get("articleId", type=int),
            'search': request.args.get("search", type=str),
            'parent_id': request.args.get("parentId", type=int)
        }

        logger.info(f"Getting comments with filters: {filters}")
        
        result = comment_service.get_comments_with_filters(filters)
        
        return handle_service_response(
            result,
            "Comments retrieved successfully",
            "Failed to retrieve comments"
        )
        
    except Exception as e:
        logger.error(f"Error in get_comments endpoint: {str(e)}")
        return APIResponse.error(
            "Internal server error",
            str(e),
            HTTPStatus.INTERNAL_SERVER_ERROR
        )


@comments_bp.route("/comments/<int:comment_id>", methods=["GET"])
def get_comment(comment_id):
    """Get a specific comment by ID"""
    try:
        if comment_id is None:
            return APIResponse.error(
                "Comment ID is required",
                status_code=HTTPStatus.BAD_REQUEST
            )

        style = request.args.get("style")
        includes = request.args.getlist("includes")

        logger.info(f"Getting comment {comment_id}")
        
        result = comment_service.get_comment_by_id(comment_id, style, includes)
        
        return handle_service_response(
            result,
            f"Comment {comment_id} retrieved successfully",
            "Failed to retrieve comment"
        )
        
    except Exception as e:
        logger.error(f"Error in get_comment endpoint: {str(e)}")
        return APIResponse.error(
            "Internal server error",
            str(e),
            HTTPStatus.INTERNAL_SERVER_ERROR
        )


@comments_bp.route("/comments", methods=["POST"])
@jwt_required()
def create_comment():
    """Create a new comment"""
    try:
        current_user_id, current_user_email = get_current_user_info()
        data = request.get_json()

        if not data:
            return APIResponse.error(
                "No data provided",
                status_code=HTTPStatus.BAD_REQUEST
            )

        logger.info(f"Creating comment by user {current_user_email}")
        
        result = comment_service.create_comment(data, current_user_email)
        
        return handle_service_response(
            result,
            "Comment created successfully",
            "Failed to create comment",
            HTTPStatus.CREATED
        )
        
    except Exception as e:
        logger.error(f"Error in create_comment endpoint: {str(e)}")
        return APIResponse.error(
            "Internal server error",
            str(e),
            HTTPStatus.INTERNAL_SERVER_ERROR
        )


@comments_bp.route("/comments/<int:comment_id>", methods=["PUT"])
@jwt_required()
def update_comment(comment_id):
    """Update an existing comment"""
    try:
        current_user_id, current_user_email = get_current_user_info()
        data = request.get_json()

        logger.info(f"Updating comment {comment_id} by user {current_user_email}")
        
        result = comment_service.update_comment(comment_id, data, current_user_id)
        
        return handle_service_response(
            result,
            "Comment updated successfully",
            "Failed to update comment"
        )
        
    except Exception as e:
        logger.error(f"Error in update_comment endpoint: {str(e)}")
        return APIResponse.error(
            "Internal server error",
            str(e),
            HTTPStatus.INTERNAL_SERVER_ERROR
        )


@comments_bp.route("/comments/<int:comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(comment_id):
    """Delete a comment (soft delete)"""
    try:
        current_user_id, current_user_email = get_current_user_info()

        logger.info(f"Deleting comment {comment_id} by user {current_user_email}")
        
        result = comment_service.delete_comment(comment_id, current_user_id)
        
        return handle_service_response(
            result,
            "Comment deleted successfully",
            "Failed to delete comment"
        )
        
    except Exception as e:
        logger.error(f"Error in delete_comment endpoint: {str(e)}")
        return APIResponse.error(
            "Internal server error",
            str(e),
            HTTPStatus.INTERNAL_SERVER_ERROR
        )
