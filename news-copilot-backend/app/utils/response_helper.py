from typing import Any, Dict, List, Optional, Union
from http import HTTPStatus
from flask import jsonify, Response


class APIResponse:
    """Enhanced API response helper class"""
    
    @staticmethod
    def success(
        message: str = "Success",
        data: Any = None,
        status_code: HTTPStatus = HTTPStatus.OK,
        metadata: Dict[str, Any] = None
    ) -> tuple[Response, int]:
        """Create a success response"""
        response_data = {
            "statusCode": status_code.value,
            "message": message,
            "success": True
        }
        
        if data is not None:
            response_data["data"] = data
        
        if metadata:
            response_data["metadata"] = metadata
        
        return jsonify(response_data), status_code.value
    
    @staticmethod
    def error(
        message: str = "An error occurred",
        error_details: Union[str, List[Dict[str, str]]] = None,
        status_code: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR,
        error_code: str = None
    ) -> tuple[Response, int]:
        """Create an error response"""
        response_data = {
            "statusCode": status_code.value,
            "message": message,
            "success": False
        }
        
        if error_details:
            if isinstance(error_details, str):
                response_data["error"] = error_details
            elif isinstance(error_details, list):
                response_data["errors"] = error_details
        
        if error_code:
            response_data["errorCode"] = error_code
        
        return jsonify(response_data), status_code.value
    
    @staticmethod
    def validation_error(
        errors: List[Dict[str, str]],
        message: str = "Validation failed"
    ) -> tuple[Response, int]:
        """Create a validation error response"""
        return APIResponse.error(
            message=message,
            error_details=errors,
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR"
        )
    
    @staticmethod
    def not_found(
        message: str = "Resource not found",
        resource_type: str = None
    ) -> tuple[Response, int]:
        """Create a not found response"""
        if resource_type:
            message = f"{resource_type} not found"
        
        return APIResponse.error(
            message=message,
            status_code=HTTPStatus.NOT_FOUND,
            error_code="NOT_FOUND"
        )
    
    @staticmethod
    def unauthorized(
        message: str = "Unauthorized access"
    ) -> tuple[Response, int]:
        """Create an unauthorized response"""
        return APIResponse.error(
            message=message,
            status_code=HTTPStatus.UNAUTHORIZED,
            error_code="UNAUTHORIZED"
        )
    
    @staticmethod
    def forbidden(
        message: str = "Access forbidden",
        required_permissions: List[str] = None
    ) -> tuple[Response, int]:
        """Create a forbidden response"""
        error_details = message
        if required_permissions:
            error_details = f"{message}. Required permissions: {', '.join(required_permissions)}"
        
        return APIResponse.error(
            message=message,
            error_details=error_details,
            status_code=HTTPStatus.FORBIDDEN,
            error_code="FORBIDDEN"
        )
    
    @staticmethod
    def created(
        message: str = "Resource created successfully",
        data: Any = None
    ) -> tuple[Response, int]:
        """Create a resource created response"""
        return APIResponse.success(
            message=message,
            data=data,
            status_code=HTTPStatus.CREATED
        )
    
    @staticmethod
    def paginated(
        items: List[Any],
        page: int,
        limit: int,
        total_count: int,
        message: str = "Items retrieved successfully",
        additional_metadata: Dict[str, Any] = None
    ) -> tuple[Response, int]:
        """Create a paginated response"""
        total_pages = (total_count + limit - 1) // limit if limit > 0 else 1
        
        metadata = {
            "pagination": {
                "page": page,
                "limit": limit,
                "totalCount": total_count,
                "totalPages": total_pages,
                "hasNext": page < total_pages,
                "hasPrevious": page > 1,
                "nextPage": page + 1 if page < total_pages else None,
                "previousPage": page - 1 if page > 1 else None
            }
        }
        
        if additional_metadata:
            metadata.update(additional_metadata)
        
        return APIResponse.success(
            message=message,
            data={"items": items},
            metadata=metadata
        )


class ResponseFormatter:
    """Legacy response formatter for backward compatibility"""
    
    @staticmethod
    def format_response(status_code: int, message: str, data: Any = None) -> Dict[str, Any]:
        """Format a standard response"""
        response = {
            "statusCode": status_code,
            "message": message
        }
        if data is not None:
            response["data"] = data
        return response
    
    @staticmethod
    def format_error_response(status_code: int, message: str, error: str = None) -> Dict[str, Any]:
        """Format an error response"""
        response = {
            "statusCode": status_code,
            "message": message
        }
        if error:
            response["error"] = error
        return response
    
    @staticmethod
    def format_validation_error(errors: List[Dict[str, str]]) -> Dict[str, Any]:
        """Format validation error response"""
        return {
            "statusCode": HTTPStatus.UNPROCESSABLE_ENTITY,
            "message": "Validation failed",
            "errors": errors
        }
