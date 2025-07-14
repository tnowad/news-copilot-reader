from typing import Dict, Any, List, Optional
from datetime import datetime

from app.models.article import Article
from app.models.category import Category
from app.models.user import User
from app.services.base_service import BaseService
from app.extensions import db


class ArticleService(BaseService):
    """Enhanced service for article operations"""
    
    def __init__(self):
        super().__init__(Article)
    
    def create_article(self, data: Dict[str, Any], author_id: int) -> Dict[str, Any]:
        """Create a new article with enhanced validation"""
        try:
            # Validate required fields
            required_fields = ['title', 'content']
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                return self._format_error_response(
                    400,
                    "Missing required fields",
                    f"Required fields: {', '.join(missing_fields)}"
                )
            
            # Generate slug if not provided
            if not data.get('slug'):
                from app.utils.slug import generate_slug
                data['slug'] = generate_slug(data['title'])
            
            # Create article
            article = Article(
                title=data['title'],
                content=data['content'],
                summary=data.get('summary', ''),
                slug=data['slug'],
                cover_image=data.get('coverImage'),
                author_id=author_id
            )
            
            # Add categories if provided
            if data.get('categoryIds'):
                categories = Category.query.filter(Category.id.in_(data['categoryIds'])).all()
                article.categories.extend(categories)
            
            db.session.add(article)
            db.session.commit()
            
            return self._format_response(
                201,
                "Article created successfully",
                self._serialize_detailed(article)
            )
            
        except Exception as e:
            db.session.rollback()
            return self._format_error_response(500, "Failed to create article", str(e))
    
    def get_articles_with_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Get articles with advanced filtering"""
        try:
            query = Article.query.filter(Article.deleted_at.is_(None))
            
            # Search filter
            if filters.get('search'):
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    Article.title.ilike(search_term) |
                    Article.summary.ilike(search_term) |
                    Article.content.ilike(search_term)
                )
            
            # Category filter
            if filters.get('categoryIds'):
                query = query.join(Article.categories).filter(
                    Category.id.in_(filters['categoryIds'])
                )
            
            # Author filter
            if filters.get('authorId'):
                query = query.filter(Article.author_id == filters['authorId'])
            
            # Date range filter
            if filters.get('startDate'):
                start_date = datetime.fromisoformat(filters['startDate'])
                query = query.filter(Article.created_at >= start_date)
            
            if filters.get('endDate'):
                end_date = datetime.fromisoformat(filters['endDate'])
                query = query.filter(Article.created_at <= end_date)
            
            # Apply sorting
            sort_by = filters.get('sortBy', 'created_at')
            sort_order = filters.get('sortOrder', 'desc')
            
            if hasattr(Article, sort_by):
                column = getattr(Article, sort_by)
                if sort_order.lower() == 'desc':
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())
            
            # Pagination
            page = filters.get('page', 1)
            limit = filters.get('limit', 10)
            
            total_count = query.count()
            offset = (page - 1) * limit
            articles = query.offset(offset).limit(limit).all()
            
            # Serialize articles
            style = filters.get('style', 'summary')
            includes = filters.get('includes', [])
            
            if style == 'full':
                serialized_articles = [self._serialize_detailed(article, includes) for article in articles]
            else:
                serialized_articles = [self._serialize(article, includes) for article in articles]
            
            metadata = {
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "totalCount": total_count,
                    "totalPages": (total_count + limit - 1) // limit,
                    "hasNext": offset + limit < total_count,
                    "hasPrevious": page > 1
                },
                "filters": filters,
                "sorting": {
                    "sortBy": sort_by,
                    "sortOrder": sort_order
                }
            }
            
            return self._format_response(
                200,
                "Articles retrieved successfully",
                {
                    "articles": serialized_articles,
                    "metadata": metadata
                }
            )
            
        except Exception as e:
            return self._format_error_response(500, "Failed to retrieve articles", str(e))
    
    def get_trending_articles(self, days: int = 7, limit: int = 10) -> Dict[str, Any]:
        """Get trending articles based on views and engagement"""
        try:
            from datetime import datetime, timedelta
            from sqlalchemy import func
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Query articles with view counts
            query = db.session.query(
                Article,
                func.count(Article.views).label('view_count'),
                func.count(Article.comments).label('comment_count')
            ).outerjoin(Article.views).outerjoin(Article.comments)\
             .filter(Article.deleted_at.is_(None))\
             .filter(Article.created_at >= cutoff_date)\
             .group_by(Article.id)\
             .order_by(
                 (func.count(Article.views) * 0.7 + func.count(Article.comments) * 0.3).desc()
             ).limit(limit)
            
            results = query.all()
            
            trending_articles = []
            for article, view_count, comment_count in results:
                article_data = self._serialize(article)
                article_data['stats'] = {
                    'viewCount': view_count,
                    'commentCount': comment_count,
                    'engagementScore': view_count * 0.7 + comment_count * 0.3
                }
                trending_articles.append(article_data)
            
            return self._format_response(
                200,
                "Trending articles retrieved successfully",
                {"articles": trending_articles}
            )
            
        except Exception as e:
            return self._format_error_response(500, "Failed to retrieve trending articles", str(e))
    
    def _serialize(self, article: Article, includes: List[str] = None) -> Dict[str, Any]:
        """Serialize article to dictionary"""
        includes = includes or []
        
        data = {
            "id": article.id,
            "title": article.title,
            "summary": article.summary,
            "slug": article.slug,
            "coverImage": article.cover_image,
            "createdAt": article.created_at.isoformat() if article.created_at else None,
            "updatedAt": article.updated_at.isoformat() if article.updated_at else None
        }
        
        if "author" in includes:
            data["author"] = {
                "id": article.author.id,
                "email": article.author.email,
                "displayName": article.author.display_name,
                "avatarImage": article.author.avatar_image
            }
        
        if "categories" in includes:
            data["categories"] = [
                {
                    "id": category.id,
                    "title": category.title,
                    "slug": category.slug
                }
                for category in article.categories
            ]
        
        if "comments" in includes:
            data["comments"] = [
                {
                    "id": comment.id,
                    "content": comment.content,
                    "createdAt": comment.created_at.isoformat() if comment.created_at else None,
                    "author": {
                        "id": comment.author.id,
                        "displayName": comment.author.display_name,
                        "avatarImage": comment.author.avatar_image
                    }
                }
                for comment in article.comments
            ]
        
        return data
    
    def _serialize_detailed(self, article: Article, includes: List[str] = None) -> Dict[str, Any]:
        """Serialize article with full details"""
        data = self._serialize(article, includes)
        data.update({
            "content": article.content,
            "deletedAt": article.deleted_at.isoformat() if article.deleted_at else None
        })
        return data
