"""
Category Service Layer
Handles all category-related business logic with enhanced functionality.
"""

from http import HTTPStatus
from typing import Dict, Any, Optional
from sqlalchemy import and_, or_, desc, asc
from datetime import datetime

from app.services.base_service import BaseService
from app.models.category import Category
from app.models.article import Article
from app.utils.database_utils import DatabaseUtils
from app.utils.error_handler import ValidationException, NotFoundError
from app.utils.slug import generate_slug


class CategoryService(BaseService):
    """Enhanced Category service with comprehensive business logic"""
    
    def __init__(self):
        super().__init__(Category)
        self.db_utils = DatabaseUtils()
    
    def get_categories_with_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get categories with advanced filtering, sorting, and pagination
        
        Args:
            filters: Dictionary containing filter parameters
            
        Returns:
            Dict containing categories data and metadata
        """
        try:
            # Build base query
            query = self.model.query
            
            # Apply search filter
            if filters.get('search'):
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        self.model.title.ilike(search_term),
                        self.model.description.ilike(search_term)
                    )
                )
            
            # Apply status filter if model has deleted_at
            if hasattr(self.model, 'deleted_at'):
                if filters.get('status') == 'deleted':
                    query = query.filter(self.model.deleted_at.isnot(None))
                else:
                    query = query.filter(self.model.deleted_at.is_(None))
            
            # Apply sorting
            sort_column = getattr(self.model, filters.get('sort_by', 'title'), self.model.title)
            if filters.get('sort_order', 'asc').lower() == 'desc':
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
            
            # Get total count before pagination
            total_categories = query.count()
            
            # Apply pagination
            page = filters.get('page', 1)
            limit = min(filters.get('limit', 10), 100)  # Cap at 100
            offset = (page - 1) * limit
            
            categories = query.offset(offset).limit(limit).all()
            
            # Serialize categories
            categories_data = []
            for category in categories:
                category_data = self._serialize_category(category, filters.get('style'), filters.get('includes', []))
                categories_data.append(category_data)
            
            # Build metadata
            metadata = self._build_pagination_metadata(
                page=page,
                limit=limit,
                offset=offset,
                total_count=total_categories,
                has_next=len(categories) == limit,
                filters=filters
            )
            
            return {
                'statusCode': 200,
                'message': 'Categories retrieved successfully',
                'data': {
                    'categories': categories_data,
                    'totalCategories': total_categories,
                    'metadata': metadata
                }
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'message': f'Failed to retrieve categories: {str(e)}',
                'data': {}
            }
    
    def get_category_by_id(self, category_id: int, includes: Optional[list] = None) -> Dict[str, Any]:
        """
        Get category by ID with optional includes
        
        Args:
            category_id: Category ID
            includes: List of related data to include
            
        Returns:
            Dict containing category data
        """
        try:
            category = self.get_by_id(category_id)
            if not category:
                raise NotFoundError(f"Category with ID {category_id} not found")
            
            # Check if soft deleted
            if hasattr(category, 'deleted_at') and category.deleted_at:
                raise NotFoundError(f"Category with ID {category_id} not found")
            
            category_data = self._serialize_category(category, style='full', includes=includes or [])
            
            return {
                'statusCode': 200,
                'message': 'Category retrieved successfully',
                'data': {
                    'category': category_data
                }
            }
            
        except NotFoundError as e:
            return {
                'statusCode': 404,
                'message': str(e),
                'data': {}
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'message': f'Failed to retrieve category: {str(e)}',
                'data': {}
            }
    
    def create_category(self, data: Dict[str, Any], created_by_email: str) -> Dict[str, Any]:
        """
        Create a new category with validation
        
        Args:
            data: Category data
            created_by_email: Email of the user creating the category
            
        Returns:
            Dict containing created category data
        """
        try:
            # Validate required fields
            if not data.get('title'):
                raise ValidationException(
                    message="Title is required",
                    errors=[{"field": "title", "message": "Title is required"}]
                )
            
            # Generate slug if not provided
            slug = data.get('slug') or generate_slug(data['title'])
            
            # Check for duplicate slug
            existing_category = self.model.query.filter_by(slug=slug).first()
            if existing_category:
                raise ValidationException(
                    message="Category with this slug already exists",
                    errors=[{"field": "slug", "message": "Slug must be unique"}]
                )
            
            # Create category data
            category_data = {
                'title': data['title'].strip(),
                'slug': slug,
                'description': data.get('description', '').strip(),
            }
            
            # Add timestamps if model supports them
            if hasattr(self.model, 'created_at'):
                category_data['created_at'] = datetime.utcnow()
            if hasattr(self.model, 'updated_at'):
                category_data['updated_at'] = datetime.utcnow()
            
            # Create category
            category = self.create(category_data)
            
            category_response = self._serialize_category(category)
            
            return {
                'statusCode': 201,
                'message': 'Category created successfully',
                'data': {
                    'category': category_response
                }
            }
            
        except ValidationException as e:
            return {
                'statusCode': 422,
                'message': e.message,
                'errors': e.errors,
                'data': {}
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'message': f'Failed to create category: {str(e)}',
                'data': {}
            }
    
    def update_category(self, category_id: int, data: Dict[str, Any], updated_by_email: str) -> Dict[str, Any]:
        """
        Update category with validation
        
        Args:
            category_id: Category ID
            data: Update data
            updated_by_email: Email of the user updating the category
            
        Returns:
            Dict containing updated category data
        """
        try:
            category = self.get_by_id(category_id)
            if not category:
                raise NotFoundError(f"Category with ID {category_id} not found")
            
            # Check if soft deleted
            if hasattr(category, 'deleted_at') and category.deleted_at:
                raise NotFoundError(f"Category with ID {category_id} not found")
            
            # Validate and prepare update data
            update_data = {}
            
            if 'title' in data:
                if not data['title'].strip():
                    raise ValidationException(
                        message="Title cannot be empty",
                        errors=[{"field": "title", "message": "Title is required"}]
                    )
                update_data['title'] = data['title'].strip()
            
            if 'description' in data:
                update_data['description'] = data['description'].strip()
            
            if 'slug' in data:
                new_slug = data['slug'].strip()
                # Check for duplicate slug (excluding current category)
                existing_category = self.model.query.filter(
                    and_(
                        self.model.slug == new_slug,
                        self.model.id != category_id
                    )
                ).first()
                if existing_category:
                    raise ValidationException(
                        message="Category with this slug already exists",
                        errors=[{"field": "slug", "message": "Slug must be unique"}]
                    )
                update_data['slug'] = new_slug
            
            # Add updated timestamp if model supports it
            if hasattr(self.model, 'updated_at'):
                update_data['updated_at'] = datetime.utcnow()
            
            # Update category
            updated_category = self.update(category_id, update_data)
            
            category_response = self._serialize_category(updated_category)
            
            return {
                'statusCode': 200,
                'message': 'Category updated successfully',
                'data': {
                    'category': category_response
                }
            }
            
        except NotFoundError as e:
            return {
                'statusCode': 404,
                'message': str(e),
                'data': {}
            }
        except ValidationException as e:
            return {
                'statusCode': 422,
                'message': e.message,
                'errors': e.errors,
                'data': {}
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'message': f'Failed to update category: {str(e)}',
                'data': {}
            }
    
    def delete_category(self, category_id: int, deleted_by_email: str) -> Dict[str, Any]:
        """
        Delete category (soft delete if supported, hard delete otherwise)
        
        Args:
            category_id: Category ID
            deleted_by_email: Email of the user deleting the category
            
        Returns:
            Dict containing deletion result
        """
        try:
            category = self.get_by_id(category_id)
            if not category:
                raise NotFoundError(f"Category with ID {category_id} not found")
            
            # Check if already soft deleted
            if hasattr(category, 'deleted_at') and category.deleted_at:
                raise NotFoundError(f"Category with ID {category_id} not found")
            
            # Check if category has articles
            article_count = Article.query.filter_by(category_id=category_id).count()
            if article_count > 0:
                return {
                    'statusCode': 409,
                    'message': f'Cannot delete category. It has {article_count} associated articles.',
                    'data': {}
                }
            
            # Perform deletion
            if hasattr(self.model, 'deleted_at'):
                # Soft delete
                self.soft_delete(category_id)
                message = 'Category soft deleted successfully'
            else:
                # Hard delete
                self.delete(category_id)
                message = 'Category deleted successfully'
            
            return {
                'statusCode': 200,
                'message': message,
                'data': {
                    'categoryId': category_id,
                    'deletedAt': datetime.utcnow().isoformat()
                }
            }
            
        except NotFoundError as e:
            return {
                'statusCode': 404,
                'message': str(e),
                'data': {}
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'message': f'Failed to delete category: {str(e)}',
                'data': {}
            }
    
    def _serialize_category(self, category: Category, style: Optional[str] = None, includes: Optional[list] = None) -> Dict[str, Any]:
        """
        Serialize category to dictionary
        
        Args:
            category: Category model instance
            style: Serialization style ('full', 'minimal', etc.)
            includes: List of related data to include
            
        Returns:
            Dict containing serialized category data
        """
        includes = includes or []
        
        # Base category data
        category_data = {
            'id': category.id,
            'title': category.title,
            'slug': category.slug,
        }
        
        # Add additional fields for full style
        if style == 'full':
            category_data.update({
                'description': getattr(category, 'description', None),
            })
            
            # Add timestamps if available
            if hasattr(category, 'created_at') and category.created_at:
                category_data['createdAt'] = category.created_at.isoformat()
            if hasattr(category, 'updated_at') and category.updated_at:
                category_data['updatedAt'] = category.updated_at.isoformat()
        
        # Add articles if requested
        if 'articles' in includes and hasattr(category, 'articles'):
            category_data['articles'] = [
                {
                    'id': article.id,
                    'title': article.title,
                    'slug': getattr(article, 'slug', None),
                    'summary': getattr(article, 'summary', None),
                    'coverImage': getattr(article, 'cover_image', None),
                    'createdAt': article.created_at.isoformat() if hasattr(article, 'created_at') and article.created_at else None
                }
                for article in category.articles
                if not (hasattr(article, 'deleted_at') and article.deleted_at)
            ]
            category_data['articleCount'] = len(category_data['articles'])
        
        return category_data
    
    def _build_pagination_metadata(self, page: int, limit: int, offset: int, 
                                  total_count: int, has_next: bool, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Build pagination metadata"""
        return {
            'pagination': {
                'currentPage': page,
                'limit': limit,
                'offset': offset,
                'totalCount': total_count,
                'pageCount': (total_count + limit - 1) // limit,
                'hasNext': has_next,
                'hasPrevious': page > 1,
                'nextPage': page + 1 if has_next else None,
                'previousPage': page - 1 if page > 1 else None
            },
            'sorting': {
                'sortBy': filters.get('sort_by', 'title'),
                'sortOrder': filters.get('sort_order', 'asc')
            },
            'filtering': {
                'search': filters.get('search'),
                'status': filters.get('status'),
                'style': filters.get('style'),
                'includes': filters.get('includes', [])
            }
        }
