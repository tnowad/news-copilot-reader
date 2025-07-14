from typing import Dict, Any, Optional, List
from http import HTTPStatus
import logging

from app.services.base_service import BaseService
from app.models.article import Article
from app.extensions import cache

logger = logging.getLogger(__name__)


class RecommendationService(BaseService):
    """Service for managing article recommendations"""
    
    def __init__(self):
        super().__init__(Article)
    
    def get_recommended_articles(self, user_id: int = None, article_id: int = None, 
                               limit: int = 10, style: str = "compact", 
                               includes: List[str] = None) -> Dict[str, Any]:
        """Get article recommendations using hybrid recommender"""
        try:
            includes = includes or []
            
            # Build cache key
            cache_key = f"recommendations:{user_id}:{article_id}:{limit}:{style}:{'_'.join(sorted(includes))}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info(f"Returning cached recommendations for user {user_id}")
                return cached_result

            # Import recommender (lazy loading)
            try:
                from app.services.recommender.recommender import hybrid_recommender
            except ImportError as e:
                logger.error(f"Failed to import recommender: {str(e)}")
                return self._format_error_response(
                    HTTPStatus.SERVICE_UNAVAILABLE,
                    "Recommendation service unavailable",
                    "Recommender system is not available"
                )

            # Get recommendations from hybrid recommender
            try:
                recommendations_data = hybrid_recommender.recommend_articles(
                    user_id, article_id, limit
                )
                
                if not recommendations_data:
                    logger.info(f"No recommendations found for user {user_id}, article {article_id}")
                    return self._format_response(
                        HTTPStatus.OK,
                        "No recommendations available",
                        {"articles": [], "metadata": self._build_metadata(user_id, article_id, limit, style, includes)}
                    )
                
            except Exception as e:
                logger.error(f"Error getting recommendations from hybrid recommender: {str(e)}")
                return self._format_error_response(
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    "Failed to generate recommendations",
                    str(e)
                )

            # Fetch articles based on recommendations
            try:
                articles = Article.query.filter(Article.id.in_(recommendations_data)).all()
                
                if not articles:
                    logger.warning(f"No articles found for recommendations: {recommendations_data}")
                    return self._format_response(
                        HTTPStatus.OK,
                        "No articles available for recommendations",
                        {"articles": [], "metadata": self._build_metadata(user_id, article_id, limit, style, includes)}
                    )
                
            except Exception as e:
                logger.error(f"Error fetching recommended articles: {str(e)}")
                return self._format_error_response(
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    "Failed to fetch recommended articles",
                    str(e)
                )

            # Serialize articles
            articles_data = []
            for article in articles:
                try:
                    article_info = self._serialize_article(article, style, includes)
                    articles_data.append(article_info)
                except Exception as e:
                    logger.warning(f"Failed to serialize article {article.id}: {str(e)}")
                    continue

            # Build metadata
            metadata = self._build_metadata(user_id, article_id, limit, style, includes)

            result = self._format_response(
                HTTPStatus.OK,
                "Recommendations retrieved successfully",
                {"articles": articles_data, "metadata": metadata}
            )

            # Cache the result for 10 minutes (recommendations can be cached longer)
            cache.set(cache_key, result, timeout=600)

            logger.info(f"Retrieved {len(articles_data)} recommended articles for user {user_id}")
            return result

        except Exception as e:
            logger.error(f"Error retrieving recommendations: {str(e)}")
            return self._format_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Failed to retrieve recommendations",
                str(e)
            )

    def _serialize_article(self, article: Article, style: str = "compact", includes: List[str] = None) -> Dict[str, Any]:
        """Serialize article data for recommendations"""
        includes = includes or []
        
        article_info = {
            "id": article.id,
            "title": article.title,
            "summary": article.summary,
            "coverImage": article.cover_image,
            "slug": article.slug,
            "createdAt": article.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
        }

        # Add full style information
        if style == "full":
            article_info.update({
                "content": article.content,
                "updatedAt": (
                    article.updated_at.strftime("%Y-%m-%dT%H:%M:%S")
                    if article.updated_at else None
                ),
                "deletedAt": (
                    article.deleted_at.strftime("%Y-%m-%dT%H:%M:%S")
                    if article.deleted_at else None
                )
            })

        # Add optional includes
        if "comments" in includes:
            article_info["comments"] = [
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

        if "categories" in includes:
            article_info["categories"] = [
                {
                    "id": category.id,
                    "title": category.title,
                    "slug": category.slug,
                }
                for category in article.categories
            ]

        if "author" in includes:
            article_info["author"] = {
                "id": article.author.id,
                "email": article.author.email,
                "displayName": article.author.display_name,
                "avatarImage": article.author.avatar_image,
            }

        return article_info

    def _build_metadata(self, user_id: int, article_id: int, limit: int, 
                       style: str, includes: List[str]) -> Dict[str, Any]:
        """Build metadata for recommendations response"""
        return {
            "pagination": {
                "limit": limit,
            },
            "style": style,
            "includes": includes,
            "filters": {
                "userId": user_id,
                "articleId": article_id,
            },
            "algorithm": "hybrid_recommender",
            "cached": False  # Will be updated if served from cache
        }

    def get_recommendation_health(self) -> Dict[str, Any]:
        """Health check for recommendation service"""
        try:
            # Check if recommender is available
            try:
                from app.services.recommender.recommender import hybrid_recommender
                recommender_available = True
                recommender_error = None
            except ImportError as e:
                recommender_available = False
                recommender_error = str(e)

            # Check cache availability
            try:
                cache.get("health_check")
                cache_available = True
                cache_error = None
            except Exception as e:
                cache_available = False
                cache_error = str(e)

            # Check database connectivity
            try:
                Article.query.count()
                database_available = True
                database_error = None
            except Exception as e:
                database_available = False
                database_error = str(e)

            # Determine overall health
            overall_healthy = recommender_available and cache_available and database_available

            health_data = {
                "service": "recommendations",
                "status": "healthy" if overall_healthy else "unhealthy",
                "timestamp": self._get_current_timestamp(),
                "components": {
                    "recommender": {
                        "status": "available" if recommender_available else "unavailable",
                        "error": recommender_error
                    },
                    "cache": {
                        "status": "available" if cache_available else "unavailable", 
                        "error": cache_error
                    },
                    "database": {
                        "status": "available" if database_available else "unavailable",
                        "error": database_error
                    }
                },
                "features": {
                    "article_recommendations": "enabled" if recommender_available else "disabled",
                    "caching": "enabled" if cache_available else "disabled",
                    "hybrid_algorithm": "enabled" if recommender_available else "disabled"
                }
            }

            status_code = HTTPStatus.OK if overall_healthy else HTTPStatus.SERVICE_UNAVAILABLE

            return self._format_response(
                status_code,
                "Recommendation service health check completed",
                health_data
            )

        except Exception as e:
            logger.error(f"Error in recommendation health check: {str(e)}")
            return self._format_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Health check failed",
                str(e)
            )

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

    def _serialize(self, article: Article) -> Dict[str, Any]:
        """Basic article serialization for recommendations"""
        return {
            "id": article.id,
            "title": article.title,
            "summary": article.summary,
            "cover_image": article.cover_image,
            "slug": article.slug,
            "created_at": article.created_at.strftime("%Y-%m-%dT%H:%M:%S")
        }
