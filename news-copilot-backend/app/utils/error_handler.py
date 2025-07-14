from typing import Dict, Any, Optional
from http import HTTPStatus
import traceback
from datetime import datetime

from flask import jsonify, request, current_app
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError, DatabaseError
from flask_jwt_extended.exceptions import JWTExtendedException

from app.utils.logging import app_logger
from app.utils.response_helper import APIResponse


class CustomException(Exception):
    """Base custom exception class"""
    
    def __init__(self, message: str, status_code: int = 500, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}


class ValidationException(CustomException):
    """Exception for validation errors"""
    
    def __init__(self, message: str = "Validation failed", errors: list = None):
        super().__init__(message, HTTPStatus.UNPROCESSABLE_ENTITY, "VALIDATION_ERROR")
        self.errors = errors or []


class AuthenticationException(CustomException):
    """Exception for authentication errors"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, HTTPStatus.UNAUTHORIZED, "AUTHENTICATION_ERROR")


class AuthorizationException(CustomException):
    """Exception for authorization errors"""
    
    def __init__(self, message: str = "Access forbidden", required_permissions: list = None):
        super().__init__(message, HTTPStatus.FORBIDDEN, "AUTHORIZATION_ERROR")
        self.required_permissions = required_permissions or []


class ResourceNotFoundException(CustomException):
    """Exception for resource not found errors"""
    
    def __init__(self, resource_type: str = "Resource", resource_id: str = None):
        message = f"{resource_type} not found"
        if resource_id:
            message += f" (ID: {resource_id})"
        super().__init__(message, HTTPStatus.NOT_FOUND, "RESOURCE_NOT_FOUND")
        self.resource_type = resource_type
        self.resource_id = resource_id


class BusinessLogicException(CustomException):
    """Exception for business logic errors"""
    
    def __init__(self, message: str, error_code: str = "BUSINESS_LOGIC_ERROR"):
        super().__init__(message, HTTPStatus.BAD_REQUEST, error_code)


class ErrorHandler:
    """Enhanced error handler"""
    
    @staticmethod
    def register_error_handlers(app):
        """Register all error handlers with the Flask app"""
        
        @app.errorhandler(CustomException)
        def handle_custom_exception(error: CustomException):
            return ErrorHandler._handle_custom_exception(error)
        
        @app.errorhandler(ValidationException)
        def handle_validation_exception(error: ValidationException):
            return ErrorHandler._handle_validation_exception(error)
        
        @app.errorhandler(HTTPException)
        def handle_http_exception(error: HTTPException):
            return ErrorHandler._handle_http_exception(error)
        
        @app.errorhandler(JWTExtendedException)
        def handle_jwt_exception(error: JWTExtendedException):
            return ErrorHandler._handle_jwt_exception(error)
        
        @app.errorhandler(IntegrityError)
        def handle_integrity_error(error: IntegrityError):
            return ErrorHandler._handle_integrity_error(error)
        
        @app.errorhandler(DatabaseError)
        def handle_database_error(error: DatabaseError):
            return ErrorHandler._handle_database_error(error)
        
        @app.errorhandler(Exception)
        def handle_generic_exception(error: Exception):
            return ErrorHandler._handle_generic_exception(error)
    
    @staticmethod
    def _handle_custom_exception(error: CustomException):
        """Handle custom exceptions"""
        app_logger.log_error(error, {
            "error_code": error.error_code,
            "status_code": error.status_code,
            "details": error.details
        })
        
        return APIResponse.error(
            message=error.message,
            error_details=error.details if error.details else None,
            status_code=HTTPStatus(error.status_code),
            error_code=error.error_code
        )
    
    @staticmethod
    def _handle_validation_exception(error: ValidationException):
        """Handle validation exceptions"""
        app_logger.log_error(error, {
            "validation_errors": error.errors
        })
        
        return APIResponse.validation_error(
            errors=error.errors,
            message=error.message
        )
    
    @staticmethod
    def _handle_http_exception(error: HTTPException):
        """Handle HTTP exceptions"""
        app_logger.log_error(error, {
            "status_code": error.code,
            "description": error.description
        })
        
        return APIResponse.error(
            message=error.description or error.name,
            status_code=HTTPStatus(error.code),
            error_code=f"HTTP_{error.code}"
        )
    
    @staticmethod
    def _handle_jwt_exception(error: JWTExtendedException):
        """Handle JWT exceptions"""
        app_logger.log_error(error)
        
        error_messages = {
            "ExpiredSignatureError": "Token has expired",
            "InvalidTokenError": "Invalid token",
            "DecodeError": "Token decode error",
            "InvalidHeaderError": "Invalid token header",
            "NoAuthorizationError": "Authorization header is required",
            "CSRFError": "CSRF token error",
            "FreshTokenRequired": "Fresh token required",
            "UserLoadError": "User load error",
            "UserClaimsVerificationError": "User claims verification failed"
        }
        
        error_type = type(error).__name__
        message = error_messages.get(error_type, "Authentication error")
        
        return APIResponse.unauthorized(message=message)
    
    @staticmethod
    def _handle_integrity_error(error: IntegrityError):
        """Handle database integrity errors"""
        app_logger.log_error(error, {
            "error_type": "IntegrityError",
            "statement": str(error.statement) if hasattr(error, 'statement') else None
        })
        
        # Parse common integrity errors
        error_message = str(error.orig) if hasattr(error, 'orig') else str(error)
        
        if "UNIQUE constraint failed" in error_message:
            message = "A record with this information already exists"
        elif "FOREIGN KEY constraint failed" in error_message:
            message = "Referenced record does not exist"
        elif "NOT NULL constraint failed" in error_message:
            message = "Required field is missing"
        else:
            message = "Database constraint violation"
        
        return APIResponse.error(
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
            error_code="INTEGRITY_ERROR"
        )
    
    @staticmethod
    def _handle_database_error(error: DatabaseError):
        """Handle database errors"""
        app_logger.log_error(error, {
            "error_type": "DatabaseError"
        })
        
        return APIResponse.error(
            message="Database operation failed",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR"
        )
    
    @staticmethod
    def _handle_generic_exception(error: Exception):
        """Handle generic exceptions"""
        # Get detailed error information
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc() if current_app.debug else None,
            "request_url": request.url if request else None,
            "request_method": request.method if request else None
        }
        
        app_logger.log_error(error, error_info)
        
        # Don't expose sensitive information in production
        if current_app.debug:
            return APIResponse.error(
                message="Internal server error",
                error_details=error_info,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                error_code="INTERNAL_ERROR"
            )
        else:
            return APIResponse.error(
                message="An unexpected error occurred",
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                error_code="INTERNAL_ERROR"
            )


class ErrorContext:
    """Context manager for handling errors in specific operations"""
    
    def __init__(self, operation_name: str, user_id: Optional[int] = None):
        self.operation_name = operation_name
        self.user_id = user_id
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            duration = (datetime.utcnow() - self.start_time).total_seconds()
            
            app_logger.log_error(exc_val, {
                "operation": self.operation_name,
                "user_id": self.user_id,
                "duration": duration,
                "error_type": exc_type.__name__
            })
        
        return False  # Don't suppress the exception
