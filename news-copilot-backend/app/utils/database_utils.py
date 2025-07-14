from typing import Dict, Any, List, Optional, Type, Callable
from datetime import datetime
from contextlib import contextmanager

from sqlalchemy import text, and_, or_
from sqlalchemy.orm import Query
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db


class DatabaseUtils:
    """Enhanced database utilities for common operations"""
    
    @staticmethod
    @contextmanager
    def transaction():
        """Context manager for database transactions"""
        try:
            yield db.session
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        finally:
            db.session.close()
    
    @staticmethod
    def bulk_create(model_class: Type[db.Model], data_list: List[Dict[str, Any]]) -> List[db.Model]:
        """Bulk create records"""
        try:
            instances = []
            for data in data_list:
                instance = model_class(**data)
                instances.append(instance)
            
            db.session.bulk_save_objects(instances)
            db.session.commit()
            return instances
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def bulk_update(model_class: Type[db.Model], updates: List[Dict[str, Any]], 
                   id_field: str = 'id') -> int:
        """Bulk update records"""
        try:
            updated_count = 0
            for update_data in updates:
                if id_field not in update_data:
                    continue
                
                record_id = update_data.pop(id_field)
                count = db.session.query(model_class)\
                    .filter(getattr(model_class, id_field) == record_id)\
                    .update(update_data)
                updated_count += count
            
            db.session.commit()
            return updated_count
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def soft_delete_bulk(model_class: Type[db.Model], ids: List[int]) -> int:
        """Bulk soft delete records"""
        try:
            if not hasattr(model_class, 'deleted_at'):
                raise ValueError(f"{model_class.__name__} does not support soft delete")
            
            count = db.session.query(model_class)\
                .filter(model_class.id.in_(ids))\
                .update({"deleted_at": datetime.utcnow()})
            
            db.session.commit()
            return count
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def execute_raw_query(query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute raw SQL query and return results as dictionaries"""
        try:
            result = db.session.execute(text(query), params or {})
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]
            
        except Exception as e:
            raise e
    
    @staticmethod
    def get_table_stats(table_name: str) -> Dict[str, Any]:
        """Get basic statistics for a table"""
        try:
            # Get row count
            count_query = f"SELECT COUNT(*) as total_count FROM {table_name}"
            count_result = DatabaseUtils.execute_raw_query(count_query)
            total_count = count_result[0]['total_count'] if count_result else 0
            
            # Get soft deleted count if applicable
            soft_deleted_count = 0
            try:
                deleted_query = f"SELECT COUNT(*) as deleted_count FROM {table_name} WHERE deleted_at IS NOT NULL"
                deleted_result = DatabaseUtils.execute_raw_query(deleted_query)
                soft_deleted_count = deleted_result[0]['deleted_count'] if deleted_result else 0
            except:
                pass  # Table might not have deleted_at column
            
            return {
                "table_name": table_name,
                "total_count": total_count,
                "active_count": total_count - soft_deleted_count,
                "soft_deleted_count": soft_deleted_count
            }
            
        except Exception as e:
            raise e


class QueryBuilder:
    """Advanced query builder for complex database operations"""
    
    def __init__(self, model_class: Type[db.Model]):
        self.model_class = model_class
        self.query = db.session.query(model_class)
        self._filters = []
        self._joins = []
        self._order_by = []
        self._group_by = []
    
    def filter_by(self, **kwargs) -> 'QueryBuilder':
        """Add filter conditions"""
        for key, value in kwargs.items():
            if hasattr(self.model_class, key):
                self._filters.append(getattr(self.model_class, key) == value)
        return self
    
    def filter_in(self, field: str, values: List[Any]) -> 'QueryBuilder':
        """Add IN filter condition"""
        if hasattr(self.model_class, field):
            self._filters.append(getattr(self.model_class, field).in_(values))
        return self
    
    def filter_like(self, field: str, pattern: str) -> 'QueryBuilder':
        """Add LIKE filter condition"""
        if hasattr(self.model_class, field):
            self._filters.append(getattr(self.model_class, field).ilike(f"%{pattern}%"))
        return self
    
    def filter_date_range(self, field: str, start_date: datetime = None, 
                         end_date: datetime = None) -> 'QueryBuilder':
        """Add date range filter"""
        if hasattr(self.model_class, field):
            column = getattr(self.model_class, field)
            if start_date:
                self._filters.append(column >= start_date)
            if end_date:
                self._filters.append(column <= end_date)
        return self
    
    def exclude_soft_deleted(self) -> 'QueryBuilder':
        """Exclude soft deleted records"""
        if hasattr(self.model_class, 'deleted_at'):
            self._filters.append(self.model_class.deleted_at.is_(None))
        return self
    
    def join_with(self, related_model: Type[db.Model], 
                  join_condition: Callable = None) -> 'QueryBuilder':
        """Add join with related model"""
        if join_condition:
            self._joins.append((related_model, join_condition))
        else:
            self._joins.append((related_model, None))
        return self
    
    def order_by(self, field: str, direction: str = 'asc') -> 'QueryBuilder':
        """Add order by clause"""
        if hasattr(self.model_class, field):
            column = getattr(self.model_class, field)
            if direction.lower() == 'desc':
                self._order_by.append(column.desc())
            else:
                self._order_by.append(column.asc())
        return self
    
    def group_by(self, field: str) -> 'QueryBuilder':
        """Add group by clause"""
        if hasattr(self.model_class, field):
            self._group_by.append(getattr(self.model_class, field))
        return self
    
    def build(self) -> Query:
        """Build the final query"""
        query = self.query
        
        # Apply joins
        for join_info in self._joins:
            if len(join_info) == 2 and join_info[1] is not None:
                query = query.join(join_info[0], join_info[1])
            else:
                query = query.join(join_info[0])
        
        # Apply filters
        if self._filters:
            query = query.filter(and_(*self._filters))
        
        # Apply group by
        if self._group_by:
            query = query.group_by(*self._group_by)
        
        # Apply order by
        if self._order_by:
            query = query.order_by(*self._order_by)
        
        return query
    
    def paginate(self, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """Execute query with pagination"""
        query = self.build()
        total_count = query.count()
        
        offset = (page - 1) * limit
        items = query.offset(offset).limit(limit).all()
        
        return {
            "items": items,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_count": total_count,
                "total_pages": (total_count + limit - 1) // limit,
                "has_next": offset + limit < total_count,
                "has_previous": page > 1
            }
        }
    
    def count(self) -> int:
        """Get count of matching records"""
        return self.build().count()
    
    def first(self) -> Optional[db.Model]:
        """Get first matching record"""
        return self.build().first()
    
    def all(self) -> List[db.Model]:
        """Get all matching records"""
        return self.build().all()


class DatabaseHealthCheck:
    """Database health monitoring utilities"""
    
    @staticmethod
    def check_connection() -> Dict[str, Any]:
        """Check database connection health"""
        try:
            # Simple query to test connection
            result = db.session.execute(text("SELECT 1"))
            result.fetchone()
            
            return {
                "status": "healthy",
                "message": "Database connection is working",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def get_database_info() -> Dict[str, Any]:
        """Get database information"""
        try:
            # Get database version
            version_result = db.session.execute(text("SELECT sqlite_version()"))
            version = version_result.fetchone()[0]
            
            return {
                "database_type": "SQLite",
                "version": version,
                "status": "connected",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "database_type": "Unknown",
                "version": "Unknown",
                "status": f"error: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
