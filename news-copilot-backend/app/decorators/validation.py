from functools import wraps
from http import HTTPStatus
from typing import Dict, Any, List, Callable

from flask import jsonify, request
from marshmallow import ValidationError as MarshmallowValidationError


def validate_json(schema_class):
    """Decorator to validate JSON request data using Marshmallow schema"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                data = request.get_json()
                if not data:
                    return jsonify({
                        "statusCode": HTTPStatus.BAD_REQUEST,
                        "message": "Request body must be valid JSON",
                        "errors": [{"field": "body", "message": "Request body is required"}]
                    }), HTTPStatus.BAD_REQUEST
                
                schema = schema_class()
                validated_data = schema.load(data)
                request.validated_data = validated_data
                return func(*args, **kwargs)
                
            except MarshmallowValidationError as e:
                errors = []
                for field, messages in e.messages.items():
                    if isinstance(messages, list):
                        for message in messages:
                            errors.append({"field": field, "message": message})
                    else:
                        errors.append({"field": field, "message": str(messages)})
                
                return jsonify({
                    "statusCode": HTTPStatus.UNPROCESSABLE_ENTITY,
                    "message": "Validation failed",
                    "errors": errors
                }), HTTPStatus.UNPROCESSABLE_ENTITY
                
            except Exception as e:
                return jsonify({
                    "statusCode": HTTPStatus.BAD_REQUEST,
                    "message": "Invalid request format",
                    "error": str(e)
                }), HTTPStatus.BAD_REQUEST
                
        return wrapper
    return decorator


def validate_query_params(validators: Dict[str, Callable]):
    """Decorator to validate query parameters"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            errors = []
            validated_params = {}
            
            for param_name, validator in validators.items():
                param_value = request.args.get(param_name)
                if param_value is not None:
                    try:
                        validated_params[param_name] = validator(param_value)
                    except (ValueError, TypeError) as e:
                        errors.append({
                            "field": param_name,
                            "message": f"Invalid {param_name}: {str(e)}"
                        })
            
            if errors:
                return jsonify({
                    "statusCode": HTTPStatus.BAD_REQUEST,
                    "message": "Invalid query parameters",
                    "errors": errors
                }), HTTPStatus.BAD_REQUEST
            
            request.validated_params = validated_params
            return func(*args, **kwargs)
            
        return wrapper
    return decorator


def require_fields(required_fields: List[str]):
    """Decorator to ensure required fields are present in JSON request"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            data = request.get_json()
            if not data:
                return jsonify({
                    "statusCode": HTTPStatus.BAD_REQUEST,
                    "message": "Request body is required",
                    "errors": [{"field": "body", "message": "Request body is required"}]
                }), HTTPStatus.BAD_REQUEST
            
            missing_fields = []
            for field in required_fields:
                if field not in data or data[field] is None:
                    missing_fields.append({"field": field, "message": f"{field} is required"})
            
            if missing_fields:
                return jsonify({
                    "statusCode": HTTPStatus.UNPROCESSABLE_ENTITY,
                    "message": "Missing required fields",
                    "errors": missing_fields
                }), HTTPStatus.UNPROCESSABLE_ENTITY
            
            return func(*args, **kwargs)
            
        return wrapper
    return decorator
