from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from http import HTTPStatus

from app.extensions import db


class BaseService(ABC):
    """Base service class with common CRUD operations"""
    
    def __init__(self, model_class):
        self.model_class = model_class
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record"""
        try:
            instance = self.model_class(**data)
            db.session.add(instance)
            db.session.commit()
            return self._format_response(
                HTTPStatus.CREATED,
                "Record created successfully",
                self._serialize(instance)
            )
        except Exception as e:
            db.session.rollback()
            return self._format_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Failed to create record",
                str(e)
            )
    
    def get_by_id(self, record_id: int) -> Dict[str, Any]:
        """Get a record by ID"""
        try:
            instance = self.model_class.query.get(record_id)
            if not instance:
                return self._format_error_response(
                    HTTPStatus.NOT_FOUND,
                    f"{self.model_class.__name__} not found"
                )
            
            return self._format_response(
                HTTPStatus.OK,
                f"{self.model_class.__name__} retrieved successfully",
                self._serialize(instance)
            )
        except Exception as e:
            return self._format_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Failed to retrieve record",
                str(e)
            )
    
    def update(self, record_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a record"""
        try:
            instance = self.model_class.query.get(record_id)
            if not instance:
                return self._format_error_response(
                    HTTPStatus.NOT_FOUND,
                    f"{self.model_class.__name__} not found"
                )
            
            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            
            db.session.commit()
            return self._format_response(
                HTTPStatus.OK,
                f"{self.model_class.__name__} updated successfully",
                self._serialize(instance)
            )
        except Exception as e:
            db.session.rollback()
            return self._format_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Failed to update record",
                str(e)
            )
    
    def soft_delete(self, record_id: int) -> Dict[str, Any]:
        """Soft delete a record (if model supports it)"""
        try:
            instance = self.model_class.query.get(record_id)
            if not instance:
                return self._format_error_response(
                    HTTPStatus.NOT_FOUND,
                    f"{self.model_class.__name__} not found"
                )
            
            if hasattr(instance, 'deleted_at'):
                from datetime import datetime
                instance.deleted_at = datetime.utcnow()
                db.session.commit()
                return self._format_response(
                    HTTPStatus.OK,
                    f"{self.model_class.__name__} deleted successfully"
                )
            else:
                # Hard delete if soft delete not supported
                db.session.delete(instance)
                db.session.commit()
                return self._format_response(
                    HTTPStatus.OK,
                    f"{self.model_class.__name__} deleted successfully"
                )
        except Exception as e:
            db.session.rollback()
            return self._format_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Failed to delete record",
                str(e)
            )
    
    def get_paginated(self, page: int = 1, limit: int = 10, filters: Dict[str, Any] = None,
                     sort_by: str = None, sort_order: str = "asc") -> Dict[str, Any]:
        """Get paginated records with filtering and sorting"""
        try:
            query = self.model_class.query
            
            # Apply soft delete filter if model supports it
            if hasattr(self.model_class, 'deleted_at'):
                query = query.filter(self.model_class.deleted_at.is_(None))
            
            # Apply filters
            if filters:
                query = self._apply_filters(query, filters)
            
            # Apply sorting
            if sort_by and hasattr(self.model_class, sort_by):
                column = getattr(self.model_class, sort_by)
                if sort_order.lower() == "desc":
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())
            
            # Get total count
            total_count = query.count()
            
            # Apply pagination
            offset = (page - 1) * limit
            instances = query.offset(offset).limit(limit).all()
            
            # Prepare metadata
            metadata = {
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "totalCount": total_count,
                    "totalPages": (total_count + limit - 1) // limit,
                    "hasNext": offset + limit < total_count,
                    "hasPrevious": page > 1
                },
                "filters": filters or {},
                "sorting": {
                    "sortBy": sort_by,
                    "sortOrder": sort_order
                }
            }
            
            return self._format_response(
                HTTPStatus.OK,
                f"{self.model_class.__name__}s retrieved successfully",
                {
                    "items": [self._serialize(instance) for instance in instances],
                    "metadata": metadata
                }
            )
        except Exception as e:
            return self._format_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Failed to retrieve records",
                str(e)
            )
    
    @abstractmethod
    def _serialize(self, instance) -> Dict[str, Any]:
        """Serialize model instance to dictionary"""
        pass
    
    def _apply_filters(self, query, filters: Dict[str, Any]):
        """Apply filters to query - override in subclasses for custom filtering"""
        return query
    
    def _format_response(self, status_code: int, message: str, data: Any = None) -> Dict[str, Any]:
        """Format standard API response"""
        response = {
            "statusCode": status_code,
            "message": message
        }
        if data is not None:
            response["data"] = data
        return response
    
    def _format_error_response(self, status_code: int, message: str, error: str = None) -> Dict[str, Any]:
        """Format error response"""
        response = {
            "statusCode": status_code,
            "message": message
        }
        if error:
            response["error"] = error
        return response
