import logging
import time
from datetime import datetime
from functools import wraps
from typing import Dict, Any, Optional
import json

from flask import request, g
from flask_jwt_extended import get_jwt_identity


class LogLevel:
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Logger:
    """Enhanced logging service"""
    
    def __init__(self, name: str = __name__):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create handler if not exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_request(self, level: str = LogLevel.INFO, additional_data: Dict[str, Any] = None):
        """Log HTTP request details"""
        try:
            user_id = None
            try:
                user_email = get_jwt_identity()
                if user_email:
                    # You might want to cache this or get from g.current_user
                    from app.models.user import User
                    user = User.query.filter_by(email=user_email).first()
                    if user:
                        user_id = user.id
            except:
                pass
            
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "method": request.method,
                "url": request.url,
                "path": request.path,
                "remote_addr": request.remote_addr,
                "user_agent": request.headers.get('User-Agent'),
                "user_id": user_id,
                "request_id": getattr(g, 'request_id', None)
            }
            
            if additional_data:
                log_data.update(additional_data)
            
            self.logger.log(getattr(logging, level), f"REQUEST: {json.dumps(log_data)}")
            
        except Exception as e:
            self.logger.error(f"Failed to log request: {e}")
    
    def log_response(self, status_code: int, response_time: float, additional_data: Dict[str, Any] = None):
        """Log HTTP response details"""
        try:
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "status_code": status_code,
                "response_time": response_time,
                "request_id": getattr(g, 'request_id', None)
            }
            
            if additional_data:
                log_data.update(additional_data)
            
            level = LogLevel.INFO if status_code < 400 else LogLevel.ERROR
            self.logger.log(getattr(logging, level), f"RESPONSE: {json.dumps(log_data)}")
            
        except Exception as e:
            self.logger.error(f"Failed to log response: {e}")
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log error with context"""
        try:
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "error_type": type(error).__name__,
                "error_message": str(error),
                "request_id": getattr(g, 'request_id', None)
            }
            
            if context:
                log_data.update(context)
            
            self.logger.error(f"ERROR: {json.dumps(log_data)}")
            
        except Exception as e:
            self.logger.error(f"Failed to log error: {e}")
    
    def log_business_event(self, event_type: str, data: Dict[str, Any]):
        """Log business events for analytics"""
        try:
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "request_id": getattr(g, 'request_id', None),
                **data
            }
            
            self.logger.info(f"EVENT: {json.dumps(log_data)}")
            
        except Exception as e:
            self.logger.error(f"Failed to log business event: {e}")


# Global logger instance
app_logger = Logger("news_copilot")


def log_execution_time(logger: Logger = None):
    """Decorator to log function execution time"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                log_data = {
                    "function": func.__name__,
                    "execution_time": execution_time,
                    "success": True
                }
                
                if logger:
                    logger.log_business_event("function_execution", log_data)
                else:
                    app_logger.log_business_event("function_execution", log_data)
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                log_data = {
                    "function": func.__name__,
                    "execution_time": execution_time,
                    "success": False,
                    "error": str(e)
                }
                
                if logger:
                    logger.log_business_event("function_execution", log_data)
                    logger.log_error(e, {"function": func.__name__})
                else:
                    app_logger.log_business_event("function_execution", log_data)
                    app_logger.log_error(e, {"function": func.__name__})
                
                raise
                
        return wrapper
    return decorator


def log_api_call(logger: Logger = None):
    """Decorator to log API calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Log request
            if logger:
                logger.log_request()
            else:
                app_logger.log_request()
            
            try:
                result = func(*args, **kwargs)
                response_time = time.time() - start_time
                
                # Extract status code from result
                status_code = 200
                if isinstance(result, tuple) and len(result) > 1:
                    status_code = result[1]
                
                # Log response
                if logger:
                    logger.log_response(status_code, response_time)
                else:
                    app_logger.log_response(status_code, response_time)
                
                return result
                
            except Exception as e:
                response_time = time.time() - start_time
                
                if logger:
                    logger.log_response(500, response_time, {"error": str(e)})
                    logger.log_error(e)
                else:
                    app_logger.log_response(500, response_time, {"error": str(e)})
                    app_logger.log_error(e)
                
                raise
                
        return wrapper
    return decorator


class PerformanceMonitor:
    """Performance monitoring service"""
    
    def __init__(self):
        self.metrics = {
            "request_count": 0,
            "error_count": 0,
            "total_response_time": 0,
            "slow_requests": 0  # requests > 2 seconds
        }
    
    def record_request(self, response_time: float, status_code: int):
        """Record request metrics"""
        self.metrics["request_count"] += 1
        self.metrics["total_response_time"] += response_time
        
        if status_code >= 400:
            self.metrics["error_count"] += 1
        
        if response_time > 2.0:
            self.metrics["slow_requests"] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        if self.metrics["request_count"] > 0:
            avg_response_time = self.metrics["total_response_time"] / self.metrics["request_count"]
            error_rate = (self.metrics["error_count"] / self.metrics["request_count"]) * 100
        else:
            avg_response_time = 0
            error_rate = 0
        
        return {
            **self.metrics,
            "average_response_time": avg_response_time,
            "error_rate": error_rate
        }
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics = {
            "request_count": 0,
            "error_count": 0,
            "total_response_time": 0,
            "slow_requests": 0
        }


# Global performance monitor
performance_monitor = PerformanceMonitor()
