from http import HTTPStatus

from flask import Blueprint, request, g
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.decorators.authorization import role_required
from app.extensions import cache
from app.models.category import Category
from app.models.role import RoleEnum
from app.services.category_service import CategoryService
from app.utils.response_helper import APIResponse
from app.utils.logging import app_logger, log_api_call
from app.utils.error_handler import ValidationException
from app.decorators.validation import require_fields

categories_bp = Blueprint("categories", __name__)
category_service = CategoryService()


def get_current_user_email():
    """Helper function to get current user email"""
    return get_jwt_identity()


def invalidate_categories_cache():
    """Helper function to invalidate categories cache"""
    try:
        cache.delete_many('categories:*')
        app_logger.log_business_event("cache_invalidated", {"cache_pattern": "categories:*"})
    except Exception as e:
        app_logger.log_error(e, {"action": "cache_invalidation", "pattern": "categories:*"})


def handle_service_response(result, success_message, error_message, success_status=HTTPStatus.OK):
    """Helper function to handle service responses consistently"""
    if result['statusCode'] == success_status.value:
        return APIResponse.success(
            message=success_message,
            data=result.get('data'),
            status_code=success_status
        )
    else:
        return APIResponse.error(
            message=error_message,
            error_details=result.get('message'),
            status_code=HTTPStatus(result['statusCode'])
        )


@categories_bp.route("/categories", methods=["GET"])
@log_api_call()
def get_categories():
    """Enhanced get categories endpoint with service layer integration"""
    try:
        # Extract and validate query parameters
        filters = {
            'page': request.args.get("page", type=int) or 1,
            'limit': request.args.get("limit", type=int) or 10,
            'sort_by': request.args.get("sortBy", type=str) or 'title',
            'sort_order': request.args.get("sortOrder", type=str) or 'asc',
            'style': request.args.get("style", type=str),
            'includes': request.args.getlist("includes"),
            'search': request.args.get("search", type=str)
        }

        # Check cache first
        cache_key = f"categories:{hash(str(sorted(filters.items())))}"
        cached_result = cache.get(cache_key)
        if cached_result:
            app_logger.log_cache_hit("categories_list", cache_key)
            return APIResponse.success(
                message="Categories retrieved successfully (cached)",
                data=cached_result
            )

        # Use service layer to get categories
        categories_result = category_service.get_categories_with_filters(filters)
        
        if categories_result['statusCode'] != 200:
            return handle_service_response(
                categories_result,
                "Categories retrieved successfully",
                "Failed to retrieve categories"
            )

        # Cache the result
        cache.set(cache_key, categories_result['data'], timeout=300)  # 5 minutes

        app_logger.log_business_event("categories_list_viewed", {
            "filters": filters,
            "total_results": categories_result['data']['totalCategories'],
            "cache_key": cache_key
        })

        return APIResponse.success(
            message="Categories retrieved successfully",
            data=categories_result['data']
        )
        
    except Exception as e:
        app_logger.log_error(e, {"endpoint": "get_categories"})
        return APIResponse.error(
            message="Failed to retrieve categories",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@categories_bp.route("/categories/<int:category_id>", methods=["GET"])
@log_api_call()
def get_category(category_id):
    """Enhanced get category by ID endpoint with service layer integration"""
    try:
        # Use service layer to get category by ID
        category_result = category_service.get_category_by_id(category_id)
        
        if category_result['statusCode'] != 200:
            return handle_service_response(
                category_result,
                "Category retrieved successfully",
                "Failed to retrieve category"
            )

        app_logger.log_business_event("category_viewed", {
            "category_id": category_id,
            "viewer_id": getattr(g, 'current_user', {}).get('id') if hasattr(g, 'current_user') else None
        })

        return APIResponse.success(
            message="Category retrieved successfully",
            data=category_result['data']
        )
        
    except Exception as e:
        app_logger.log_error(e, {
            "endpoint": "get_category",
            "category_id": category_id
        })
        return APIResponse.error(
            message="Failed to retrieve category",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@categories_bp.route("/categories", methods=["POST"])
@jwt_required()
@role_required([RoleEnum.ADMIN])
@log_api_call()
@require_fields(['title'])
def create_category():
    """Enhanced create category endpoint with service layer integration"""
    try:
        data = request.get_json()
        current_user_email = get_current_user_email()
        
        # Use service layer to create category
        create_result = category_service.create_category(data, current_user_email)
        
        if create_result['statusCode'] != 201:
            return handle_service_response(
                create_result,
                "Category created successfully",
                "Failed to create category",
                HTTPStatus.CREATED
            )

        # Invalidate categories cache
        invalidate_categories_cache()

        app_logger.log_business_event("category_created", {
            "category_id": create_result['data']['category']['id'],
            "created_by": current_user_email,
            "title": data.get('title')
        })

        return handle_service_response(
            create_result,
            "Category created successfully",
            "Failed to create category",
            HTTPStatus.CREATED
        )
        
    except ValidationException as e:
        return APIResponse.validation_error(e.errors, e.message)
    except Exception as e:
        app_logger.log_error(e, {
            "endpoint": "create_category",
            "current_user": get_current_user_email(),
            "data": locals().get('data', {})
        })
        return APIResponse.error(
            message="Failed to create category",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@categories_bp.route("/categories/<int:category_id>", methods=["PUT"])
@jwt_required() 
@role_required([RoleEnum.ADMIN])
@log_api_call()
def update_category(category_id):
    """Enhanced update category endpoint with service layer integration"""
    try:
        data = request.get_json()
        current_user_email = get_current_user_email()
        
        # Use service layer to update category
        update_result = category_service.update_category(category_id, data, current_user_email)
        
        if update_result['statusCode'] != 200:
            return handle_service_response(
                update_result,
                "Category updated successfully",
                "Failed to update category"
            )

        # Invalidate categories cache
        invalidate_categories_cache()

        app_logger.log_business_event("category_updated", {
            "category_id": category_id,
            "updated_by": current_user_email,
            "fields_updated": list(data.keys()) if data else []
        })

        return handle_service_response(
            update_result,
            "Category updated successfully",
            "Failed to update category"
        )
        
    except ValidationException as e:
        return APIResponse.validation_error(e.errors, e.message)
    except Exception as e:
        app_logger.log_error(e, {
            "endpoint": "update_category",
            "category_id": category_id,
            "current_user": get_current_user_email()
        })
        return APIResponse.error(
            message="Failed to update category",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@categories_bp.route("/categories/<int:category_id>", methods=["DELETE"])
@jwt_required()
@role_required([RoleEnum.ADMIN])
@log_api_call()
def delete_category(category_id):
    """Enhanced delete category endpoint with service layer integration"""
    try:
        current_user_email = get_current_user_email()
        
        # Use service layer to delete category
        delete_result = category_service.delete_category(category_id, current_user_email)
        
        if delete_result['statusCode'] != 200:
            return handle_service_response(
                delete_result,
                "Category deleted successfully",
                "Failed to delete category"
            )

        # Invalidate categories cache
        invalidate_categories_cache()

        app_logger.log_business_event("category_deleted", {
            "category_id": category_id,
            "deleted_by": current_user_email
        })

        return handle_service_response(
            delete_result,
            "Category deleted successfully",
            "Failed to delete category"
        )
        
    except Exception as e:
        app_logger.log_error(e, {
            "endpoint": "delete_category",
            "category_id": category_id,
            "current_user": get_current_user_email()
        })
        return APIResponse.error(
            message="Failed to delete category",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@categories_bp.route("/categories/health", methods=["GET"])
@log_api_call()
def categories_health_check():
    """Health check endpoint for categories service"""
    try:
        # Basic health checks
        total_categories = Category.query.count()
        active_categories = Category.query.filter(Category.deleted_at.is_(None)).count() if hasattr(Category, 'deleted_at') else total_categories
        
        # Recent activity
        from datetime import datetime, timedelta
        last_24h = datetime.utcnow() - timedelta(hours=24)
        recent_categories = Category.query.filter(Category.created_at >= last_24h).count() if hasattr(Category, 'created_at') else 0
        
        health_data = {
            "service": "categories",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "statistics": {
                "totalCategories": total_categories,
                "activeCategories": active_categories,
                "recentCategories24h": recent_categories
            },
            "features": {
                "categoryListing": "enabled",
                "categoryCreation": "enabled",
                "categoryUpdating": "enabled",
                "categoryDeletion": "enabled",
                "caching": "enabled"
            }
        }
        
        return APIResponse.success(
            message="Categories service is healthy",
            data=health_data
        )
        
    except Exception as e:
        app_logger.log_error(e, {"endpoint": "categories_health_check"})
        return APIResponse.error(
            message="Categories service health check failed",
            error_details=str(e),
            status_code=HTTPStatus.SERVICE_UNAVAILABLE
        )
