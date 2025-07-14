from datetime import datetime
from http import HTTPStatus
from typing import List

from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.decorators.authorization import role_required, ownership_required
from app.decorators.validation import require_fields, validate_query_params
from app.extensions import db
from app.models.article import Article
from app.models.bookmark import Bookmark
from app.models.category import Category
from app.models.role import RoleEnum
from app.models.user import User
from app.services.article_service import ArticleService
from app.services.cache_service import ArticleCacheManager, cached_response
from app.utils.response_helper import APIResponse
from app.utils.logging import app_logger, log_api_call
from app.utils.error_handler import ResourceNotFoundException, ValidationException

articles_bp = Blueprint("articles", __name__)
article_service = ArticleService()


def serialize_article(article, style='summary', includes=None):
    """
    DRY helper: Serialize article data consistently across endpoints
    
    Args:
        article: Article model instance
        style: 'summary' or 'full'
        includes: List of related data to include
    
    Returns:
        Dict containing serialized article data
    """
    includes = includes or []
    
    # Base article data
    article_data = {
        "id": article.id,
        "title": article.title,
        "summary": article.summary,
        "coverImage": article.cover_image,
        "slug": article.slug,
        "createdAt": article.created_at.isoformat() if article.created_at else None,
    }
    
    # Add full content and timestamps for full style
    if style == "full":
        article_data.update({
            "content": article.content,
            "updatedAt": article.updated_at.isoformat() if article.updated_at else None,
            "deletedAt": article.deleted_at.isoformat() if article.deleted_at else None
        })
    
    # Add related data based on includes
    if "categories" in includes and hasattr(article, 'categories'):
        article_data["categories"] = [
            {
                "id": category.id,
                "title": category.title,
                "slug": category.slug,
            }
            for category in article.categories
        ]
    
    if "author" in includes and hasattr(article, 'author'):
        article_data["author"] = {
            "id": article.author.id,
            "email": article.author.email,
            "displayName": article.author.display_name,
            "avatarImage": article.author.avatar_image,
        }
    
    if "comments" in includes and hasattr(article, 'comments'):
        article_data["comments"] = [
            {
                "id": comment.id,
                "content": comment.content,
                "createdAt": comment.created_at.isoformat() if comment.created_at else None,
                "updatedAt": comment.updated_at.isoformat() if comment.updated_at else None,
                "parentCommentId": comment.parent_id,
                "author": {
                    "id": comment.author.id,
                    "email": comment.author.email,
                    "displayName": comment.author.display_name,
                    "avatarImage": comment.author.avatar_image,
                },
            }
            for comment in article.comments
        ]
    
    return article_data


def get_current_user_info():
    """DRY helper: Get current user information for logging"""
    return getattr(g, 'current_user', {}).get('id') if hasattr(g, 'current_user') else None


def handle_permission_check(article, current_user, action="access"):
    """
    DRY helper: Check user permissions for article operations
    
    Args:
        article: Article model instance
        current_user: Current user object
        action: Type of action ('access', 'modify', 'delete')
    
    Returns:
        Tuple of (is_allowed: bool, error_response: APIResponse or None)
    """
    if not article or (hasattr(article, 'deleted_at') and article.deleted_at):
        return False, APIResponse.not_found("Article", str(article.id if article else "unknown"))
    
    if action in ['modify', 'delete']:
        is_admin = any(str(role.name) == str(RoleEnum.ADMIN) for role in current_user.roles)
        if article.author_id != current_user.id and not is_admin:
            action_verb = "modify" if action == "modify" else "delete"
            return False, APIResponse.forbidden(
                message=f"You can only {action_verb} your own articles",
                required_permissions=["ADMIN", "OWNER"]
            )
    
    return True, None


@articles_bp.route("/articles", methods=["GET"])
@log_api_call()
@cached_response(timeout=1800, key_prefix="articles_list")  # 30 minutes cache
@validate_query_params({
    'page': lambda x: max(1, int(x)),
    'limit': lambda x: min(100, max(1, int(x))),  # Max 100 items per page
    'sortBy': str,
    'sortOrder': lambda x: x if x in ['asc', 'desc'] else 'desc'
})
def get_articles():
    """Enhanced get articles endpoint using service layer"""
    try:
        # Extract and validate query parameters
        filters = {
            'page': request.args.get('page', 1, type=int),
            'limit': request.args.get('limit', 10, type=int),
            'search': request.args.get('search', type=str),
            'categoryIds': request.args.getlist('categoryIds', type=int),
            'authorId': request.args.get('authorId', type=int),
            'sortBy': request.args.get('sortBy', 'created_at', type=str),
            'sortOrder': request.args.get('sortOrder', 'desc', type=str),
            'style': request.args.get('style', 'summary', type=str),
            'includes': request.args.getlist('includes', type=str),
            'startDate': request.args.get('startDate', type=str),
            'endDate': request.args.get('endDate', type=str)
        }

        # Log the request using DRY helper
        app_logger.log_business_event("articles_list_requested", {
            "filters": filters,
            "user_id": get_current_user_info()
        })

        # Use service layer to get articles
        result = article_service.get_articles_with_filters(filters)
        
        if result['statusCode'] != 200:
            return APIResponse.error(
                message=result['message'],
                error_details=result.get('error'),
                status_code=HTTPStatus(result['statusCode'])
            )

        return APIResponse.success(
            message=result['message'],
            data=result['data']
        )

    except ValidationException as e:
        return APIResponse.validation_error(e.errors, e.message)
    except Exception as e:
        app_logger.log_error(e, {"endpoint": "get_articles", "filters": locals().get('filters', {})})
        return APIResponse.error(
            message="Failed to retrieve articles",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@articles_bp.route("/articles/<int:article_id>", methods=["GET"])
@log_api_call()
@cached_response(timeout=3600, key_prefix="article_detail")  # 1 hour cache
def get_article(article_id):
    """Enhanced get single article endpoint using service layer with DRY helpers"""
    try:
        # Get article from database
        article = Article.query.get(article_id)
        if not article or (hasattr(article, 'deleted_at') and article.deleted_at):
            return APIResponse.not_found("Article", str(article_id))

        # Extract parameters
        style = request.args.get('style', 'summary')
        includes = request.args.getlist('includes')
        
        # Use DRY helper to serialize article
        article_data = serialize_article(article, style=style, includes=includes)

        # Log article view using DRY helper
        app_logger.log_business_event("article_viewed", {
            "article_id": article_id,
            "article_title": article.title,
            "user_id": get_current_user_info(),
            "includes": includes,
            "style": style
        })

        return APIResponse.success(
            message="Article retrieved successfully",
            data={"article": article_data}
        )

    except Exception as e:
        app_logger.log_error(e, {"endpoint": "get_article", "article_id": article_id})
        return APIResponse.error(
            message="Failed to retrieve article",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@articles_bp.route("/articles", methods=["POST"])
@jwt_required()
@role_required([RoleEnum.ADMIN, RoleEnum.WRITER])
@log_api_call()
@require_fields(['title', 'content'])
def create_article():
    """Enhanced create article endpoint using service layer"""
    try:
        current_user = g.current_user  # Set by role_required decorator
        data = request.get_json()

        # Validate author permissions
        author_id = data.get("authorId")
        if author_id and author_id != current_user.id:
            # Only admins can create articles for other users
            if not any(str(role.name) == str(RoleEnum.ADMIN) for role in current_user.roles):
                return APIResponse.forbidden(
                    message="Only users with ADMIN role can create articles with custom author",
                    required_permissions=["ADMIN"]
                )

        # Prepare article data
        article_data = {
            'title': data.get('title'),
            'content': data.get('content'),
            'summary': data.get('summary', ''),
            'slug': data.get('slug'),
            'coverImage': data.get('coverImage'),
            'categoryIds': data.get('categoryIds', [])
        }

        # Use service layer to create article
        result = article_service.create_article(article_data, current_user.id)
        
        if result['statusCode'] != 201:
            return APIResponse.error(
                message=result['message'],
                error_details=result.get('error'),
                status_code=HTTPStatus(result['statusCode'])
            )

        # Invalidate article caches
        ArticleCacheManager.invalidate_article_caches()

        # Log article creation
        article_data = result['data']
        app_logger.log_business_event("article_created", {
            "article_id": article_data['id'],
            "article_title": article_data['title'],
            "author_id": current_user.id,
            "categories": [cat['id'] for cat in article_data.get('categories', [])]
        })

        return APIResponse.created(
            message=result['message'],
            data=result['data']
        )

    except ValidationException as e:
        return APIResponse.validation_error(e.errors, e.message)
    except Exception as e:
        app_logger.log_error(e, {
            "endpoint": "create_article",
            "user_id": get_current_user_info(),
            "data": locals().get('data', {})
        })
        return APIResponse.error(
            message="Failed to create article",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@articles_bp.route("/articles/<int:article_id>", methods=["PUT"])
@jwt_required()
@role_required([RoleEnum.ADMIN, RoleEnum.WRITER])
@log_api_call()
def update_article(article_id):
    """Enhanced update article endpoint using service layer with DRY helpers"""
    try:
        current_user = g.current_user  # Set by role_required decorator
        data = request.get_json()

        # Get article and check permissions using DRY helper
        article = Article.query.get(article_id)
        is_allowed, error_response = handle_permission_check(article, current_user, action="modify")
        if not is_allowed:
            return error_response

        # Validate author change permissions
        new_author_id = data.get("authorId")
        if new_author_id and new_author_id != current_user.id:
            is_admin = any(str(role.name) == str(RoleEnum.ADMIN) for role in current_user.roles)
            if not is_admin:
                return APIResponse.forbidden(
                    message="Only users with ADMIN role can change article author",
                    required_permissions=["ADMIN"]
                )

        # Prepare update data (only include non-None values)
        update_data = {}
        for field in ['title', 'summary', 'slug', 'content', 'coverImage']:
            if field in data and data[field] is not None:
                update_data[field] = data[field]

        # Handle author update
        if new_author_id:
            update_data['author_id'] = new_author_id

        # Use service layer to update article
        result = article_service.update(article_id, update_data)
        
        if result['statusCode'] != 200:
            return APIResponse.error(
                message=result['message'],
                error_details=result.get('error'),
                status_code=HTTPStatus(result['statusCode'])
            )

        # Handle category updates
        category_ids = data.get('categoryIds')
        if category_ids is not None:
            article.categories.clear()
            for category_id in category_ids:
                category = Category.query.get(category_id)
                if category:
                    article.categories.append(category)
            db.session.commit()

        # Invalidate caches
        ArticleCacheManager.invalidate_article_caches(article_id)

        # Get updated article and serialize using DRY helper
        updated_article = Article.query.get(article_id)
        article_data = serialize_article(updated_article, style='full', includes=['author', 'categories'])

        # Log article update
        app_logger.log_business_event("article_updated", {
            "article_id": article_id,
            "updated_by": current_user.id,
            "updated_fields": list(update_data.keys()),
            "categories_updated": category_ids is not None
        })

        return APIResponse.success(
            message="Article updated successfully",
            data={"article": article_data}
        )

    except ValidationException as e:
        return APIResponse.validation_error(e.errors, e.message)
    except Exception as e:
        app_logger.log_error(e, {
            "endpoint": "update_article",
            "article_id": article_id,
            "user_id": get_current_user_info()
        })
        return APIResponse.error(
            message="Failed to update article",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@articles_bp.route("/articles/<int:article_id>", methods=["DELETE"])
@jwt_required()
@role_required([RoleEnum.ADMIN, RoleEnum.WRITER])
@log_api_call()
def delete_article(article_id):
    """Enhanced delete article endpoint using service layer with DRY helpers"""
    try:
        current_user = g.current_user  # Set by role_required decorator

        # Get article and check permissions using DRY helper
        article = Article.query.get(article_id)
        is_allowed, error_response = handle_permission_check(article, current_user, action="delete")
        if not is_allowed:
            return error_response

        # Store article title for logging before deletion
        article_title = article.title

        # Use service layer for soft delete
        result = article_service.soft_delete(article_id)
        
        if result['statusCode'] != 200:
            return APIResponse.error(
                message=result['message'],
                error_details=result.get('error'),
                status_code=HTTPStatus(result['statusCode'])
            )

        # Invalidate caches
        ArticleCacheManager.invalidate_article_caches(article_id)

        # Log article deletion
        app_logger.log_business_event("article_deleted", {
            "article_id": article_id,
            "article_title": article_title,
            "deleted_by": current_user.id,
            "deletion_type": "soft_delete"
        })

        return APIResponse.success(
            message="Article deleted successfully",
            data={"deletedAt": datetime.utcnow().isoformat()}
        )

    except Exception as e:
        app_logger.log_error(e, {
            "endpoint": "delete_article",
            "article_id": article_id,
            "user_id": get_current_user_info()
        })
        return APIResponse.error(
            message="Failed to delete article",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@articles_bp.route("/articles/trending", methods=["GET"])
@log_api_call()
@cached_response(timeout=900, key_prefix="trending_articles")  # 15 minutes cache
@validate_query_params({
    'days': lambda x: min(30, max(1, int(x))),  # 1-30 days
    'limit': lambda x: min(50, max(1, int(x)))   # 1-50 articles
})
def get_trending_articles():
    """Get trending articles endpoint using service layer"""
    try:
        days = request.args.get('days', 7, type=int)
        limit = request.args.get('limit', 10, type=int)

        # Use service layer to get trending articles
        result = article_service.get_trending_articles(days, limit)
        
        if result['statusCode'] != 200:
            return APIResponse.error(
                message=result['message'],
                error_details=result.get('error'),
                status_code=HTTPStatus(result['statusCode'])
            )

        # Log trending articles request using DRY helper
        app_logger.log_business_event("trending_articles_requested", {
            "days": days,
            "limit": limit,
            "user_id": get_current_user_info()
        })

        return APIResponse.success(
            message=result['message'],
            data=result['data']
        )

    except Exception as e:
        app_logger.log_error(e, {"endpoint": "get_trending_articles"})
        return APIResponse.error(
            message="Failed to retrieve trending articles",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@articles_bp.route("/articles/bookmarks", methods=["GET"])
@jwt_required()
@log_api_call()
@cached_response(timeout=300, key_prefix="user_bookmarked_articles")  # 5 minutes cache
def get_bookmarked_articles():
    """Enhanced get bookmarked articles endpoint using service layer"""
    try:
        current_user = User.query.filter_by(email=get_jwt_identity()).first_or_404()
        
        # Extract parameters
        filters = {
            'page': request.args.get('page', 1, type=int),
            'limit': request.args.get('limit', 10, type=int),
            'sortBy': request.args.get('sortBy', 'created_at', type=str),
            'sortOrder': request.args.get('sortOrder', 'desc', type=str),
            'style': request.args.get('style', 'summary', type=str),
            'includes': request.args.getlist('includes', type=str)
        }

        # Get user's bookmarked articles
        bookmarks = current_user.bookmarks
        articles = [bookmark.article for bookmark in bookmarks if bookmark.article.deleted_at is None]
        
        # Apply sorting
        sort_key = lambda article: getattr(article, filters['sortBy'], article.created_at)
        reverse_sort = filters['sortOrder'].lower() == 'desc'
        articles.sort(key=sort_key, reverse=reverse_sort)
        
        # Apply pagination
        total_articles = len(articles)
        page = filters['page']
        limit = filters['limit']
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_articles = articles[start_idx:end_idx]

        # Serialize articles using DRY helper
        articles_data = []
        for article in paginated_articles:
            article_data = serialize_article(article, style=filters['style'], includes=filters['includes'])
            articles_data.append(article_data)

        # Prepare response with pagination metadata
        return APIResponse.paginated(
            items=articles_data,
            page=page,
            limit=limit,
            total_count=total_articles,
            message="Bookmarked articles retrieved successfully",
            additional_metadata={
                "sorting": {
                    "sortBy": filters['sortBy'],
                    "sortOrder": filters['sortOrder']
                },
                "style": filters['style'],
                "includes": filters['includes']
            }
        )

    except Exception as e:
        app_logger.log_error(e, {
            "endpoint": "get_bookmarked_articles",
            "user_id": get_current_user_info()
        })
        return APIResponse.error(
            message="Failed to retrieve bookmarked articles",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )


@articles_bp.route("/articles/health", methods=["GET"])
@log_api_call()
def articles_health_check():
    """Health check endpoint for articles service"""
    try:
        # Basic health checks
        total_articles = Article.query.count()
        active_articles = Article.query.filter(Article.deleted_at.is_(None)).count()
        deleted_articles = total_articles - active_articles
        
        # Recent activity
        from datetime import datetime, timedelta
        last_24h = datetime.utcnow() - timedelta(hours=24)
        recent_articles = Article.query.filter(Article.created_at >= last_24h).count()
        
        health_data = {
            "service": "articles",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "statistics": {
                "totalArticles": total_articles,
                "activeArticles": active_articles,
                "deletedArticles": deleted_articles,
                "recentArticles24h": recent_articles
            },
            "features": {
                "caching": "enabled",
                "trending": "enabled",
                "bookmarks": "enabled",
                "softDelete": "enabled"
            }
        }
        
        return APIResponse.success(
            message="Articles service is healthy",
            data=health_data
        )
        
    except Exception as e:
        app_logger.log_error(e, {"endpoint": "articles_health_check"})
        return APIResponse.error(
            message="Articles service health check failed",
            error_details=str(e),
            status_code=HTTPStatus.SERVICE_UNAVAILABLE
        )
