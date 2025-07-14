from datetime import datetime
from http import HTTPStatus

from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)

from app.decorators.authorization import role_required
from app.extensions import db
from app.models.role import Role, RoleEnum
from app.models.user import User
from app.services.user_service import UserService
from app.utils.response_helper import APIResponse
from app.utils.logging import app_logger, log_api_call
from app.utils.error_handler import ValidationException, AuthenticationException
from app.decorators.validation import require_fields

users_bp = Blueprint("user", __name__)
user_service = UserService()


@users_bp.route("/users/profile", methods=["GET"])
@jwt_required()
@log_api_call()
def profile():
    """Enhanced user profile endpoint with service layer integration"""
    try:
        current_user_email = get_jwt_identity()
        
        # Use service layer to get user profile
        profile_result = user_service.get_user_profile(current_user_email)
        
        if profile_result['statusCode'] != 200:
            return APIResponse.error(
                message=profile_result['message'],
                status_code=HTTPStatus(profile_result['statusCode'])
            )

        user_data = profile_result['data']['user']
        
        # Check if full profile is requested
        style_param = request.args.get("style")
        if style_param == "full":
            # Get additional profile information
            extended_result = user_service.get_extended_profile(current_user_email)
            if extended_result['statusCode'] == 200:
                user_data.update(extended_result['data'])

        app_logger.log_business_event("profile_viewed", {
            "user_id": user_data.get('id'),
            "style": style_param
        })

        return APIResponse.success(
            message="User profile retrieved successfully",
            data={"user": user_data}
        )
        
    except Exception as e:
        app_logger.log_error(e, {
            "endpoint": "profile",
            "user_email": get_jwt_identity()
        })
        return APIResponse.error(
            message="Failed to retrieve user profile",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@users_bp.route("/users", methods=["GET"])
@log_api_call()
def get_users():
    """Enhanced get users endpoint with service layer integration"""
    try:
        # Extract query parameters
        filters = {
            'page': request.args.get("page", type=int) or 1,
            'limit': request.args.get("limit", type=int) or 10,
            'search': request.args.get("search", type=str),
            'sort_by': request.args.get("sortBy", type=str) or 'created_at',
            'sort_order': request.args.get("sortOrder", type=str) or 'desc',
            'role': request.args.get("role", type=str),
            'status': request.args.get("status", type=str)
        }

        # Use service layer to get users
        users_result = user_service.get_users_with_filters(filters)
        
        if users_result['statusCode'] != 200:
            return APIResponse.error(
                message=users_result['message'],
                status_code=HTTPStatus(users_result['statusCode'])
            )

        app_logger.log_business_event("users_list_viewed", {
            "filters": filters,
            "total_results": users_result['data']['totalUsers']
        })

        return APIResponse.success(
            message="Users retrieved successfully",
            data=users_result['data']
        )
        
    except Exception as e:
        app_logger.log_error(e, {"endpoint": "get_users"})
        return APIResponse.error(
            message="Failed to retrieve users",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@users_bp.route("/users/<int:user_id>", methods=["GET"])
@log_api_call()
def get_user(user_id):
    """Enhanced get user by ID endpoint with service layer integration"""
    try:
        # Use service layer to get user by ID
        user_result = user_service.get_user_by_id(user_id)
        
        if user_result['statusCode'] != 200:
            return APIResponse.error(
                message=user_result['message'],
                status_code=HTTPStatus(user_result['statusCode'])
            )

        app_logger.log_business_event("user_profile_viewed", {
            "target_user_id": user_id,
            "viewer_id": getattr(g, 'current_user', {}).get('id') if hasattr(g, 'current_user') else None
        })

        return APIResponse.success(
            message="User retrieved successfully",
            data=user_result['data']
        )
        
    except Exception as e:
        app_logger.log_error(e, {
            "endpoint": "get_user",
            "user_id": user_id
        })
        return APIResponse.error(
            message="Failed to retrieve user",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@users_bp.route("/users/health", methods=["GET"])
@log_api_call()
def users_health_check():
    """Health check endpoint for users service"""
    try:
        # Basic health checks
        total_users = User.query.count()
        active_users = User.query.filter(User.deleted_at.is_(None)).count() if hasattr(User, 'deleted_at') else total_users
        
        # Recent activity
        from datetime import datetime, timedelta
        last_24h = datetime.utcnow() - timedelta(hours=24)
        recent_users = User.query.filter(User.created_at >= last_24h).count() if hasattr(User, 'created_at') else 0
        
        health_data = {
            "service": "users",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "statistics": {
                "totalUsers": total_users,
                "activeUsers": active_users,
                "recentUsers24h": recent_users
            },
            "features": {
                "profileManagement": "enabled",
                "userListing": "enabled",
                "userDeletion": "enabled",
                "roleManagement": "enabled"
            }
        }
        
        return APIResponse.success(
            message="Users service is healthy",
            data=health_data
        )
        
    except Exception as e:
        app_logger.log_error(e, {"endpoint": "users_health_check"})
        return APIResponse.error(
            message="Users service health check failed",
            error_details=str(e),
            status_code=HTTPStatus.SERVICE_UNAVAILABLE
        )


@users_bp.route("/users", methods=["POST"])
@log_api_call()
@require_fields(['email', 'password', 'displayName'])
def create_user():
    """Enhanced create user endpoint with service layer integration"""
    try:
        data = request.get_json()
        
        # Use service layer to create user
        create_result = user_service.create_user(data)
        
        if create_result['statusCode'] != 201:
            return APIResponse.error(
                message=create_result['message'],
                status_code=HTTPStatus(create_result['statusCode'])
            )

        app_logger.log_business_event("user_created_admin", {
            "user_id": create_result['data']['user']['id'],
            "email": data.get('email')
        })

        return APIResponse.success(
            message="User created successfully",
            data=create_result['data'],
            status_code=HTTPStatus.CREATED
        )
        
    except ValidationException as e:
        return APIResponse.validation_error(e.errors, e.message)
    except Exception as e:
        app_logger.log_error(e, {
            "endpoint": "create_user",
            "data": locals().get('data', {})
        })
        return APIResponse.error(
            message="Failed to create user",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@users_bp.route("/users/profile", methods=["PUT"])
@jwt_required()
@log_api_call()
def update_profile():
    """Enhanced update profile endpoint with service layer integration"""
    try:
        current_user_email = get_jwt_identity()
        data = request.get_json()
        
        # Get current user ID
        current_user = user_service.get_user_by_email(current_user_email)
        if current_user['statusCode'] != 200:
            return APIResponse.error(
                message="Current user not found",
                status_code=HTTPStatus.UNAUTHORIZED
            )
        
        user_id = current_user['data']['user']['id']
        
        # Use service layer to update profile
        update_result = user_service.update_user_profile(
            user_id=user_id,
            current_user_email=current_user_email,
            update_data=data
        )
        
        if update_result['statusCode'] != 200:
            return APIResponse.error(
                message=update_result['message'],
                status_code=HTTPStatus(update_result['statusCode'])
            )

        app_logger.log_business_event("profile_updated", {
            "user_id": user_id,
            "fields_updated": list(data.keys()) if data else []
        })

        return APIResponse.success(
            message="Profile updated successfully",
            data=update_result['data']
        )
        
    except ValidationException as e:
        return APIResponse.validation_error(e.errors, e.message)
    except Exception as e:
        app_logger.log_error(e, {
            "endpoint": "update_profile",
            "current_user": get_jwt_identity()
        })
        return APIResponse.error(
            message="Failed to update profile",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@users_bp.route("/users/<int:user_id>", methods=["PUT"])
@jwt_required()
@log_api_call()
def update_user(user_id):
    """Enhanced update user endpoint with service layer integration"""
    try:
        current_user_email = get_jwt_identity()
        data = request.get_json()
        
        # Use service layer to update user
        update_result = user_service.update_user_profile(
            user_id=user_id,
            current_user_email=current_user_email,
            update_data=data
        )
        
        if update_result['statusCode'] != 200:
            return APIResponse.error(
                message=update_result['message'],
                status_code=HTTPStatus(update_result['statusCode'])
            )

        app_logger.log_business_event("user_profile_updated", {
            "user_id": user_id,
            "updated_by": current_user_email,
            "fields_updated": list(data.keys()) if data else []
        })

        return APIResponse.success(
            message="User updated successfully",
            data=update_result['data']
        )
        
    except ValidationException as e:
        return APIResponse.validation_error(e.errors, e.message)
    except Exception as e:
        app_logger.log_error(e, {
            "endpoint": "update_user",
            "user_id": user_id,
            "current_user": get_jwt_identity()
        })
        return APIResponse.error(
            message="Failed to update user",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@users_bp.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
@role_required([RoleEnum.ADMIN])
@log_api_call()
def delete_user(user_id):
    """Enhanced delete user endpoint with service layer integration"""
    try:
        current_user_email = get_jwt_identity()
        
        # Use service layer to delete user
        delete_result = user_service.delete_user(user_id, current_user_email)
        
        if delete_result['statusCode'] != 200:
            return APIResponse.error(
                message=delete_result['message'],
                status_code=HTTPStatus(delete_result['statusCode'])
            )

        app_logger.log_business_event("user_deleted", {
            "deleted_user_id": user_id,
            "deleted_by": current_user_email
        })

        return APIResponse.success(
            message="User deleted successfully",
            data=delete_result['data']
        )
        
    except Exception as e:
        app_logger.log_error(e, {
            "endpoint": "delete_user",
            "user_id": user_id,
            "current_user": get_jwt_identity()
        })
        return APIResponse.error(
            message="Failed to delete user",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )
