from typing import Dict, Any, Optional, List
from http import HTTPStatus
from datetime import datetime
import logging

from app.services.base_service import BaseService
from app.models.comment import Comment
from app.models.article import Article
from app.models.user import User
from app.models.role import RoleEnum
from app.extensions import db, cache

logger = logging.getLogger(__name__)


class CommentService(BaseService):
    """Service for managing comments"""
    
    def __init__(self):
        super().__init__(Comment)
    
    def get_comments_with_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Get comments with advanced filtering and pagination"""
        try:
            page = filters.get('page', 1)
            limit = filters.get('limit', 10)
            sort_by = filters.get('sort_by')
            sort_order = filters.get('sort_order')
            style = filters.get('style')
            includes = filters.get('includes', [])
            user_id = filters.get('user_id')
            article_id = filters.get('article_id')
            search = filters.get('search')
            parent_id = filters.get('parent_id')

            # Build cache key
            cache_key = f"comments:{hash(str(sorted(filters.items())))}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info("Returning cached comments")
                return cached_result

            # Build query
            query = Comment.query.filter(Comment.deleted_at.is_(None))

            # Apply filters
            if parent_id:
                query = query.filter(Comment.parent_id == parent_id)
            if user_id:
                query = query.filter(Comment.author_id == user_id)
            if article_id:
                query = query.filter(Comment.article_id == article_id)
            if search:
                query = query.filter(Comment.content.ilike(f"%{search}%"))

            # Apply sorting
            if sort_by and sort_order:
                if sort_by == "user":
                    query = query.join(User).order_by(
                        User.display_name.asc() if sort_order == "asc" else User.display_name.desc()
                    )
                elif sort_by == "article":
                    query = query.join(Article).order_by(
                        Article.title.asc() if sort_order == "asc" else Article.title.desc()
                    )
                elif sort_by == "createdAt":
                    query = query.order_by(
                        Comment.created_at.asc() if sort_order == "asc" else Comment.created_at.desc()
                    )

            # Get total count before pagination
            total_count = query.count()

            # Apply pagination
            if page and limit:
                offset = (page - 1) * limit
                query = query.offset(offset).limit(limit)

            comments = query.all()

            # Serialize comments
            comments_data = []
            for comment in comments:
                comment_info = self._serialize_comment(comment, style, includes)
                comments_data.append(comment_info)

            # Build metadata
            metadata = self._build_pagination_metadata(page, limit, total_count, sort_by, sort_order, filters)

            result = self._format_response(
                HTTPStatus.OK,
                "Comments retrieved successfully",
                {"comments": comments_data, "metadata": metadata}
            )

            # Cache the result for 5 minutes
            cache.set(cache_key, result, timeout=300)

            logger.info(f"Retrieved {len(comments_data)} comments with filters: {filters}")
            return result

        except Exception as e:
            logger.error(f"Error retrieving comments: {str(e)}")
            return self._format_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Failed to retrieve comments",
                str(e)
            )

    def get_comment_by_id(self, comment_id: int, style: str = None, includes: List[str] = None) -> Dict[str, Any]:
        """Get a specific comment by ID"""
        try:
            comment = Comment.query.get(comment_id)
            
            if not comment:
                logger.warning(f"Comment {comment_id} not found")
                return self._format_error_response(
                    HTTPStatus.NOT_FOUND,
                    "Comment not found",
                    f"Comment with id {comment_id} not found"
                )

            includes = includes or []
            comment_data = self._serialize_comment(comment, style, includes)

            # Add child comments if requested
            if "childComments" in includes and comment.child_comments:
                child_comments_data = []
                for child_comment in comment.child_comments:
                    child_comment_info = self._serialize_comment(child_comment, style, includes)
                    child_comments_data.append(child_comment_info)
                comment_data["childComments"] = child_comments_data

            logger.info(f"Retrieved comment {comment_id}")
            return self._format_response(
                HTTPStatus.OK,
                f"Comment {comment_id} retrieved successfully",
                {"comment": comment_data}
            )

        except Exception as e:
            logger.error(f"Error retrieving comment {comment_id}: {str(e)}")
            return self._format_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Failed to retrieve comment",
                str(e)
            )

    def create_comment(self, data: Dict[str, Any], current_user_email: str) -> Dict[str, Any]:
        """Create a new comment"""
        try:
            content = data.get("content")
            author_id = data.get("authorId")
            article_id = data.get("articleId")
            parent_id = data.get("parentId")

            if not all([content, author_id, article_id]):
                logger.warning("Missing required fields for comment creation")
                return self._format_error_response(
                    HTTPStatus.BAD_REQUEST,
                    "Missing required fields: content, authorId, articleId"
                )

            # Verify article exists
            article = Article.query.get(article_id)
            if not article:
                logger.warning(f"Article {article_id} not found for comment creation")
                return self._format_error_response(
                    HTTPStatus.NOT_FOUND,
                    "Article not found"
                )

            # Verify parent comment exists if provided
            if parent_id:
                parent_comment = Comment.query.get(parent_id)
                if not parent_comment:
                    logger.warning(f"Parent comment {parent_id} not found")
                    return self._format_error_response(
                        HTTPStatus.NOT_FOUND,
                        "Parent comment not found"
                    )

            comment = Comment(
                content=content,
                author_id=author_id,
                article_id=article_id,
                parent_id=parent_id,
                created_at=datetime.now()
            )

            db.session.add(comment)
            db.session.commit()

            # Clear comments cache
            cache.delete_many('comments:*')

            comment_data = self._serialize_comment(comment, includes=['author'])

            logger.info(f"Comment created successfully by user {current_user_email}")
            return self._format_response(
                HTTPStatus.CREATED,
                "Comment created successfully",
                {"comment": comment_data}
            )

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating comment: {str(e)}")
            return self._format_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Failed to create comment",
                str(e)
            )

    def update_comment(self, comment_id: int, data: Dict[str, Any], current_user_id: int) -> Dict[str, Any]:
        """Update an existing comment"""
        try:
            comment = Comment.query.get(comment_id)

            if not comment:
                logger.warning(f"Comment {comment_id} not found for update")
                return self._format_error_response(
                    HTTPStatus.NOT_FOUND,
                    "Comment not found",
                    f"Comment with id {comment_id} not found"
                )

            # Check authorization
            current_user = User.query.get(current_user_id)
            if not self._check_comment_permission(current_user, comment):
                logger.warning(f"User {current_user_id} not authorized to update comment {comment_id}")
                return self._format_error_response(
                    HTTPStatus.UNAUTHORIZED,
                    "You are not authorized to update this comment"
                )

            content = data.get("content")
            if content:
                comment.content = content
                comment.updated_at = datetime.now()

            db.session.commit()

            # Clear comments cache
            cache.delete_many('comments:*')

            comment_data = self._serialize_comment(comment)

            logger.info(f"Comment {comment_id} updated successfully by user {current_user_id}")
            return self._format_response(
                HTTPStatus.OK,
                "Comment updated successfully",
                {"comment": comment_data}
            )

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating comment {comment_id}: {str(e)}")
            return self._format_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Failed to update comment",
                str(e)
            )

    def delete_comment(self, comment_id: int, current_user_id: int) -> Dict[str, Any]:
        """Soft delete a comment"""
        try:
            comment = Comment.query.get(comment_id)

            if not comment:
                logger.warning(f"Comment {comment_id} not found for deletion")
                return self._format_error_response(
                    HTTPStatus.NOT_FOUND,
                    "Comment not found",
                    f"Comment with id {comment_id} not found"
                )

            # Check authorization
            current_user = User.query.get(current_user_id)
            if not self._check_comment_permission(current_user, comment):
                logger.warning(f"User {current_user_id} not authorized to delete comment {comment_id}")
                return self._format_error_response(
                    HTTPStatus.UNAUTHORIZED,
                    "You are not authorized to delete this comment"
                )

            # Soft delete
            comment.deleted_at = datetime.now()
            db.session.commit()

            # Clear comments cache
            cache.delete_many('comments:*')

            logger.info(f"Comment {comment_id} deleted successfully by user {current_user_id}")
            return self._format_response(
                HTTPStatus.OK,
                "Comment deleted successfully"
            )

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting comment {comment_id}: {str(e)}")
            return self._format_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Failed to delete comment",
                str(e)
            )

    def _serialize_comment(self, comment: Comment, style: str = None, includes: List[str] = None) -> Dict[str, Any]:
        """Serialize comment data"""
        includes = includes or []
        
        comment_info = {
            "id": comment.id,
            "content": comment.content,
            "parentId": comment.parent_id,
            "createdAt": comment.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
            "updatedAt": comment.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if comment.updated_at else None,
        }

        if style == "full":
            comment_info["deletedAt"] = (
                comment.deleted_at.strftime("%Y-%m-%dT%H:%M:%S") 
                if comment.deleted_at else None
            )

        if "author" in includes and comment.author:
            comment_info["author"] = {
                "id": comment.author.id,
                "email": comment.author.email,
                "displayName": comment.author.display_name,
                "avatarImage": comment.author.avatar_image,
            }

        if "article" in includes and comment.article:
            comment_info["article"] = {
                "id": comment.article.id,
                "title": comment.article.title,
                "summary": comment.article.summary,
                "createdAt": comment.article.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
                "coverImage": comment.article.cover_image,
            }

        return comment_info

    def _check_comment_permission(self, user: User, comment: Comment) -> bool:
        """Check if user has permission to modify comment"""
        if not user:
            return False
        
        # Admin can modify any comment
        if any(role.name == RoleEnum.ADMIN for role in user.roles):
            return True
        
        # User can modify their own comment
        return user.id == comment.author_id

    def _build_pagination_metadata(self, page: int, limit: int, total_count: int, 
                                 sort_by: str, sort_order: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Build pagination metadata"""
        return {
            "pagination": {
                "offset": (page - 1) * limit if (page and limit) else None,
                "limit": limit,
                "previousOffset": (page - 2) * limit if page > 1 else None,
                "nextOffset": page * limit if total_count > page * limit else None,
                "currentPage": page if page else None,
                "totalCount": total_count,
            },
            "sortedBy": {
                "name": sort_by,
                "order": sort_order,
            },
            "filters": {
                "articleId": filters.get('article_id'),
                "userId": filters.get('user_id'),
                "parentId": filters.get('parent_id'),
                "search": filters.get('search'),
            },
        }

    def _serialize(self, comment: Comment) -> Dict[str, Any]:
        """Basic comment serialization"""
        return {
            "id": comment.id,
            "content": comment.content,
            "author_id": comment.author_id,
            "article_id": comment.article_id,
            "parent_id": comment.parent_id,
            "created_at": comment.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
            "updated_at": comment.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if comment.updated_at else None
        }
