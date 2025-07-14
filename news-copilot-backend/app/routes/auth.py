from http import HTTPStatus

from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from flask_mail import Message

from app.extensions import db, cache, mail
from app.models.role import Role, RoleEnum
from app.models.user import User
from app.services.mailer import send_reset_email
from app.services.user_service import UserService
from app.utils.code import generate_random_code
from app.utils.response_helper import APIResponse
from app.utils.logging import app_logger, log_api_call
from app.utils.error_handler import ValidationException, AuthenticationException
from app.decorators.validation import require_fields

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
user_service = UserService()


@auth_bp.route("/sign-in", methods=["POST"])
@log_api_call()
@require_fields(['email', 'password'])
def sign_in():
    """Enhanced sign-in endpoint with better validation and logging"""
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        # Use the service layer for authentication
        auth_result = user_service.authenticate_user(email, password)
        
        if auth_result['statusCode'] != 200:
            return APIResponse.error(
                message=auth_result['message'],
                status_code=HTTPStatus(auth_result['statusCode'])
            )

        user_data = auth_result['data']['user']
        roles = auth_result['data']['roles']

        # Generate tokens
        access_token = create_access_token(identity=email)
        refresh_token = create_refresh_token(identity=email)

        # Log successful login
        app_logger.log_business_event("user_login", {
            "user_id": user_data['id'],
            "email": email,
            "roles": roles
        })

        return APIResponse.success(
            message="Login successful",
            data={
                "user": {
                    "id": user_data['id'],
                    "email": user_data['email'],
                    "displayName": user_data['displayName'],
                    "avatar": user_data.get('avatarImage'),
                    "roles": roles,
                },
                "token": {
                    "accessToken": access_token,
                    "refreshToken": refresh_token,
                },
            }
        )

    except Exception as e:
        app_logger.log_error(e, {"endpoint": "sign_in", "email": email})
        raise


@auth_bp.route("/sign-up", methods=["POST"])
@log_api_call()
@require_fields(['email', 'password', 'confirmPassword', 'displayName', 'acceptTerms'])
def sign_up():
    """Enhanced sign-up endpoint with service layer integration"""
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        confirm_password = data.get("confirmPassword")
        display_name = data.get("displayName")
        accept_terms = data.get("acceptTerms")

        # Password confirmation validation
        if password != confirm_password:
            raise ValidationException(
                message="Passwords do not match",
                errors=[{"field": "confirmPassword", "message": "Passwords do not match"}]
            )

        # Terms acceptance validation
        if not accept_terms:
            raise ValidationException(
                message="Terms acceptance is required",
                errors=[{"field": "acceptTerms", "message": "Terms acceptance is required"}]
            )

        # Use service layer for user registration
        registration_result = user_service.register_user(
            email=email,
            password=password,
            display_name=display_name
        )
        
        if registration_result['statusCode'] != 201:
            return APIResponse.error(
                message=registration_result['message'],
                status_code=HTTPStatus(registration_result['statusCode'])
            )

        user_data = registration_result['data']['user']

        # Log successful registration
        app_logger.log_business_event("user_registration", {
            "user_id": user_data['id'],
            "email": email,
            "display_name": display_name
        })

        return APIResponse.success(
            message="Registration successful",
            data={
                "user": {
                    "id": user_data['id'],
                    "email": user_data['email'],
                    "displayName": user_data['displayName'],
                    "roles": user_data.get('roles', [])
                }
            },
            status_code=HTTPStatus.CREATED
        )

    except ValidationException as e:
        return APIResponse.validation_error(e.errors, e.message)
    except Exception as e:
        app_logger.log_error(e, {
            "endpoint": "sign_up",
            "email": data.get("email") if 'data' in locals() else None
        })
        return APIResponse.error(
            message="Registration failed",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
@log_api_call()
def refresh():
    """Enhanced refresh token endpoint"""
    try:
        current_user_email = get_jwt_identity()
        
        # Verify user still exists and is active
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            raise AuthenticationException("User not found")
        
        new_token = create_access_token(identity=current_user_email)
        
        app_logger.log_business_event("token_refresh", {
            "user_id": user.id,
            "email": current_user_email
        })
        
        return APIResponse.success(
            message="Token refreshed successfully",
            data={
                "accessToken": new_token
            }
        )
        
    except AuthenticationException as e:
        return APIResponse.error(
            message=str(e),
            status_code=HTTPStatus.UNAUTHORIZED
        )
    except Exception as e:
        app_logger.log_error(e, {"endpoint": "refresh"})
        return APIResponse.error(
            message="Token refresh failed",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@auth_bp.route("/forgot-password", methods=["POST"])
@log_api_call()
@require_fields(['email'])
def forgot_password():
    """Enhanced forgot password endpoint"""
    try:
        data = request.get_json()
        email = data.get("email")

        # Use service layer for password reset
        reset_result = user_service.initiate_password_reset(email)
        
        if reset_result['statusCode'] != 200:
            # For security, we always return success even if user doesn't exist
            pass

        app_logger.log_business_event("password_reset_requested", {
            "email": email
        })

        return APIResponse.success(
            message="If the email exists, a password reset link has been sent",
            data={}
        )
        
    except Exception as e:
        app_logger.log_error(e, {"endpoint": "forgot_password"})
        return APIResponse.error(
            message="Password reset request failed",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@auth_bp.route("/reset-password", methods=["POST"])
@log_api_call()
@require_fields(['token', 'newPassword'])
def reset_password():
    """Enhanced reset password endpoint"""
    try:
        data = request.get_json()
        token = data.get("token")
        new_password = data.get("newPassword")

        # Use service layer for password reset
        reset_result = user_service.reset_password(token, new_password)
        
        if reset_result['statusCode'] != 200:
            return APIResponse.error(
                message=reset_result['message'],
                status_code=HTTPStatus(reset_result['statusCode'])
            )

        app_logger.log_business_event("password_reset_completed", {
            "user_id": reset_result['data']['user_id']
        })

        return APIResponse.success(
            message="Password reset successful",
            data={}
        )
        
    except ValidationException as e:
        return APIResponse.validation_error(e.errors, e.message)
    except Exception as e:
        app_logger.log_error(e, {"endpoint": "reset_password"})
        return APIResponse.error(
            message="Password reset failed",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@auth_bp.route("/auth/health", methods=["GET"])
@log_api_call()
def auth_health_check():
    """Health check endpoint for authentication service"""
    try:
        # Basic health checks
        total_users = User.query.count()
        active_users = User.query.filter(User.deleted_at.is_(None)).count() if hasattr(User, 'deleted_at') else total_users
        
        # Recent activity
        from datetime import datetime, timedelta
        last_24h = datetime.utcnow() - timedelta(hours=24)
        recent_logins = cache.get('recent_logins_count') or 0
        
        health_data = {
            "service": "authentication",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "statistics": {
                "totalUsers": total_users,
                "activeUsers": active_users,
                "recentLogins24h": recent_logins
            },
            "features": {
                "registration": "enabled",
                "login": "enabled",
                "passwordReset": "enabled",
                "tokenRefresh": "enabled"
            }
        }
        
        return APIResponse.success(
            message="Authentication service is healthy",
            data=health_data
        )
        
    except Exception as e:
        app_logger.log_error(e, {"endpoint": "auth_health_check"})
        return APIResponse.error(
            message="Authentication service health check failed",
            error_details=str(e),
            status_code=HTTPStatus.SERVICE_UNAVAILABLE
        )
