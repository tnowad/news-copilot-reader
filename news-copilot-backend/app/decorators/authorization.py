from functools import wraps
from http import HTTPStatus
from typing import List, Optional, Union

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.models.role import RoleEnum
from app.models.user import User


def role_required(roles: List[RoleEnum]):
    """Enhanced role-based authorization decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Verify JWT token is present and valid
                verify_jwt_in_request()
                current_user_email = get_jwt_identity()
                
                if not current_user_email:
                    return jsonify({
                        "statusCode": HTTPStatus.UNAUTHORIZED,
                        "message": "Invalid or expired token",
                        "error": "Authentication required"
                    }), HTTPStatus.UNAUTHORIZED
                
                user: Optional[User] = User.query.filter_by(email=current_user_email).first()

                if not user:
                    return jsonify({
                        "statusCode": HTTPStatus.UNAUTHORIZED,
                        "message": "User not found",
                        "error": "Invalid user credentials"
                    }), HTTPStatus.UNAUTHORIZED

                # Check if user has any of the required roles
                user_roles = [str(user_role.name) for user_role in user.roles]
                required_roles = [str(role.value) for role in roles]
                
                if not any(role in user_roles for role in required_roles):
                    return jsonify({
                        "statusCode": HTTPStatus.FORBIDDEN,
                        "message": "Insufficient privileges",
                        "error": f"Roles required: {', '.join(required_roles)}. Your roles: {', '.join(user_roles)}",
                        "requiredRoles": required_roles,
                        "userRoles": user_roles
                    }), HTTPStatus.FORBIDDEN

                # Add user to request context for use in the route
                from flask import g
                g.current_user = user
                
                return func(*args, **kwargs)
                
            except Exception as e:
                return jsonify({
                    "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
                    "message": "Authorization check failed",
                    "error": str(e)
                }), HTTPStatus.INTERNAL_SERVER_ERROR

        return wrapper
    return decorator


def ownership_required(get_resource_owner_id):
    """Decorator to check if user owns the resource or has admin privileges"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                current_user_email = get_jwt_identity()
                user: Optional[User] = User.query.filter_by(email=current_user_email).first()
                
                if not user:
                    return jsonify({
                        "statusCode": HTTPStatus.UNAUTHORIZED,
                        "message": "User not found"
                    }), HTTPStatus.UNAUTHORIZED
                
                # Check if user is admin (admins can access all resources)
                if any(str(role.name) == str(RoleEnum.ADMIN) for role in user.roles):
                    from flask import g
                    g.current_user = user
                    return func(*args, **kwargs)
                
                # Get the resource owner ID
                resource_owner_id = get_resource_owner_id(*args, **kwargs)
                
                if user.id != resource_owner_id:
                    return jsonify({
                        "statusCode": HTTPStatus.FORBIDDEN,
                        "message": "Access denied",
                        "error": "You can only access your own resources"
                    }), HTTPStatus.FORBIDDEN
                
                from flask import g
                g.current_user = user
                return func(*args, **kwargs)
                
            except Exception as e:
                return jsonify({
                    "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
                    "message": "Ownership check failed",
                    "error": str(e)
                }), HTTPStatus.INTERNAL_SERVER_ERROR
                
        return wrapper
    return decorator
