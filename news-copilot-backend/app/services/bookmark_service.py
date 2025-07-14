from typing import Dict, Any, Optional, List
from http import HTTPStatus
from datetime import datetime
import logging

from app.services.base_service import BaseService
from app.models.bookmark import Bookmark
from app.models.article import Article
from app.models.user import User
from app.extensions import db, cache

logger = logging.getLogger(__name__)


class BookmarkService(BaseService):
    """Service for managing bookmarks"""
    
    def __init__(self):
        super().__init__(Bookmark)
    
    def create_bookmark(self, article_id: int, user_id: int, current_user_id: int) -> Dict[str, Any]:
        """Create a new bookmark"""
        try:
            # Check authorization
            if user_id != current_user_id:
                logger.warning(f"Unauthorized bookmark creation attempt by user {current_user_id} for user {user_id}")
                return self._format_error_response(
                    HTTPStatus.UNAUTHORIZED,
                    "Unauthorized"
                )
            
            # Check if article exists
            article = Article.query.get(article_id)
            if not article:
                logger.warning(f"Bookmark creation failed: Article {article_id} not found")
                return self._format_error_response(
                    HTTPStatus.NOT_FOUND,
                    "Article not found"
                )
            
            # Check if bookmark already exists
            existing_bookmark = Bookmark.query.filter_by(
                article_id=article_id, user_id=user_id
            ).first()
            
            if existing_bookmark:
                logger.info(f"Bookmark already exists for article {article_id} and user {user_id}")
                return self._format_error_response(
                    HTTPStatus.CONFLICT,
                    "Bookmark already exists"
                )
            
            # Create bookmark
            bookmark = Bookmark(
                article_id=article_id,
                user_id=user_id,
                created_at=datetime.now()
            )
            
            db.session.add(bookmark)
            db.session.commit()
            
            # Clear user bookmarks cache
            cache.delete(f"user_bookmarks_{user_id}")
            
            logger.info(f"Bookmark created successfully for article {article_id} by user {user_id}")
            return self._format_response(
                HTTPStatus.CREATED,
                "Bookmark created successfully",
                {"id": bookmark.id}
            )
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating bookmark: {str(e)}")
            return self._format_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Failed to create bookmark",
                str(e)
            )
    
    def delete_bookmark(self, bookmark_id: int, current_user_id: int) -> Dict[str, Any]:
        """Delete a bookmark"""
        try:
            bookmark = Bookmark.query.filter_by(
                id=bookmark_id, user_id=current_user_id
            ).first()
            
            if not bookmark:
                logger.warning(f"Bookmark {bookmark_id} not found for user {current_user_id}")
                return self._format_error_response(
                    HTTPStatus.NOT_FOUND,
                    "Bookmark not found"
                )
            
            user_id = bookmark.user_id
            db.session.delete(bookmark)
            db.session.commit()
            
            # Clear user bookmarks cache
            cache.delete(f"user_bookmarks_{user_id}")
            
            logger.info(f"Bookmark {bookmark_id} deleted successfully by user {current_user_id}")
            return self._format_response(
                HTTPStatus.OK,
                "Bookmark deleted successfully"
            )
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting bookmark {bookmark_id}: {str(e)}")
            return self._format_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Failed to delete bookmark",
                str(e)
            )
    
    def get_bookmarks(self, current_user_id: int, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get bookmarks with filtering and pagination"""
        try:
            filters = filters or {}
            article_id = filters.get('article_id')
            user_id = filters.get('user_id', current_user_id)
            limit = filters.get('limit', 10)
            style = filters.get('style', 'compact')
            includes = filters.get('includes', [])
            
            # Build cache key
            cache_key = f"user_bookmarks_{user_id}_{article_id}_{limit}_{style}_{'_'.join(sorted(includes))}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info(f"Returning cached bookmarks for user {user_id}")
                return cached_result
            
            # Build query
            query = Bookmark.query
            if article_id:
                query = query.filter_by(article_id=article_id)
            
            query = query.filter_by(user_id=user_id)
            bookmarks = query.limit(limit).all()
            
            # Serialize bookmarks
            bookmark_data = []
            for bookmark in bookmarks:
                bookmark_info = self._serialize_bookmark(bookmark, includes)
                bookmark_data.append(bookmark_info)
            
            metadata = {
                "pagination": {"limit": limit},
                "style": style,
                "includes": includes,
                "filters": {
                    "userId": user_id,
                    "articleId": article_id,
                }
            }
            
            result = self._format_response(
                HTTPStatus.OK,
                "Bookmarks retrieved successfully",
                {"bookmarks": bookmark_data, "metadata": metadata}
            )
            
            # Cache the result for 5 minutes
            cache.set(cache_key, result, timeout=300)
            
            logger.info(f"Retrieved {len(bookmark_data)} bookmarks for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving bookmarks: {str(e)}")
            return self._format_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Failed to retrieve bookmarks",
                str(e)
            )
    
    def get_bookmark_by_id(self, bookmark_id: int, current_user_id: int) -> Dict[str, Any]:
        """Get a specific bookmark by ID"""
        try:
            bookmark = Bookmark.query.filter_by(
                id=bookmark_id, user_id=current_user_id
            ).first()
            
            if not bookmark:
                logger.warning(f"Bookmark {bookmark_id} not found for user {current_user_id}")
                return self._format_error_response(
                    HTTPStatus.NOT_FOUND,
                    "Bookmark not found"
                )
            
            bookmark_info = self._serialize_bookmark(bookmark, includes=['categories', 'author', 'comments'])
            
            logger.info(f"Retrieved bookmark {bookmark_id} for user {current_user_id}")
            return self._format_response(
                HTTPStatus.OK,
                "Bookmark retrieved successfully",
                {"bookmark": bookmark_info}
            )
            
        except Exception as e:
            logger.error(f"Error retrieving bookmark {bookmark_id}: {str(e)}")
            return self._format_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Failed to retrieve bookmark",
                str(e)
            )
    
    def check_marked_articles(self, article_ids: List[int], current_user_id: int) -> Dict[str, Any]:
        """Check which articles are bookmarked by the user"""
        try:
            marked_articles = Bookmark.query.filter(
                Bookmark.article_id.in_(article_ids),
                Bookmark.user_id == current_user_id
            ).all()
            
            if not marked_articles:
                logger.info(f"No bookmarked articles found for user {current_user_id}")
                return self._format_response(
                    HTTPStatus.OK,
                    "No bookmarked articles found",
                    {"bookmarks": []}
                )
            
            bookmark_data = []
            for bookmark in marked_articles:
                bookmark_info = self._serialize_bookmark(bookmark, includes=['categories', 'author', 'comments'])
                bookmark_data.append(bookmark_info)
            
            logger.info(f"Found {len(bookmark_data)} bookmarked articles for user {current_user_id}")
            return self._format_response(
                HTTPStatus.OK,
                "Bookmarked articles retrieved successfully",
                {"bookmarks": bookmark_data}
            )
            
        except Exception as e:
            logger.error(f"Error checking marked articles: {str(e)}")
            return self._format_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Failed to check marked articles",
                str(e)
            )
    
    def _serialize_bookmark(self, bookmark: Bookmark, includes: List[str] = None) -> Dict[str, Any]:
        """Serialize bookmark with related data"""
        includes = includes or []
        
        bookmark_info = {
            "id": bookmark.id,
            "user_id": bookmark.user_id,
            "article": self._serialize_article(bookmark.article, includes),
            "created_at": bookmark.created_at.strftime("%Y-%m-%dT%H:%M:%S")
        }
        
        return bookmark_info
    
    def _serialize_article(self, article: Article, includes: List[str] = None) -> Dict[str, Any]:
        """Serialize article data for bookmark"""
        includes = includes or []
        
        article_data = {
            "id": article.id,
            "title": article.title,
            "summary": article.summary,
            "coverImage": article.cover_image,
            "slug": article.slug,
            "createdAt": article.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
            "content": article.content,
            "updatedAt": (
                article.updated_at.strftime("%Y-%m-%dT%H:%M:%S")
                if article.updated_at else None
            ),
            "deletedAt": (
                article.deleted_at.strftime("%Y-%m-%dT%H:%M:%S")
                if article.deleted_at else None
            )
        }
        
        # Add optional includes
        if "categories" in includes:
            article_data["categories"] = [
                {
                    "id": category.id,
                    "title": category.title,
                    "slug": category.slug,
                }
                for category in article.categories
            ]
        
        if "author" in includes:
            article_data["author"] = {
                "id": article.author.id,
                "email": article.author.email,
                "displayName": article.author.display_name,
                "avatarImage": article.author.avatar_image,
            }
        
        if "comments" in includes:
            article_data["comments"] = [
                {
                    "id": comment.id,
                    "content": comment.content,
                    "createdAt": comment.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
                    "updatedAt": (
                        comment.updated_at.strftime("%Y-%m-%dT%H:%M:%S")
                        if comment.updated_at else None
                    ),
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
    
    def _serialize(self, bookmark: Bookmark) -> Dict[str, Any]:
        """Basic bookmark serialization"""
        return {
            "id": bookmark.id,
            "user_id": bookmark.user_id,
            "article_id": bookmark.article_id,
            "created_at": bookmark.created_at.strftime("%Y-%m-%dT%H:%M:%S")
        }
