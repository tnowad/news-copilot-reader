from typing import Dict, Any
import uuid
from datetime import datetime

from flask import request, g, Flask
from flask_jwt_extended import get_jwt_identity

from app.utils.logging import app_logger, performance_monitor


class RequestMiddleware:
    """Enhanced request middleware for logging and monitoring"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize the middleware with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_appcontext(self.teardown_request)
    
    def before_request(self):
        """Execute before each request"""
        # Generate unique request ID
        g.request_id = str(uuid.uuid4())
        g.start_time = datetime.utcnow()
        
        # Log request details
        self._log_request_start()
    
    def after_request(self, response):
        """Execute after each request"""
        # Calculate response time
        if hasattr(g, 'start_time'):
            response_time = (datetime.utcnow() - g.start_time).total_seconds()
        else:
            response_time = 0
        
        # Log response details
        self._log_request_end(response.status_code, response_time)
        
        # Record metrics
        performance_monitor.record_request(response_time, response.status_code)
        
        # Add request ID to response headers
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
        
        return response
    
    def teardown_request(self, exception=None):
        """Execute at the end of request context"""
        if exception:
            app_logger.log_error(exception, {
                "request_id": getattr(g, 'request_id', None),
                "request_teardown": True
            })
    
    def _log_request_start(self):
        """Log request start details"""
        try:
            user_id = None
            try:
                user_email = get_jwt_identity()
                if user_email:
                    from app.models.user import User
                    user = User.query.filter_by(email=user_email).first()
                    if user:
                        user_id = user.id
                        g.current_user = user
            except:
                pass
            
            request_data = {
                "request_id": g.request_id,
                "method": request.method,
                "url": request.url,
                "path": request.path,
                "remote_addr": request.remote_addr,
                "user_agent": request.headers.get('User-Agent'),
                "user_id": user_id,
                "content_type": request.content_type,
                "content_length": request.content_length
            }
            
            app_logger.log_business_event("request_start", request_data)
            
        except Exception as e:
            app_logger.log_error(e, {"context": "request_start_logging"})
    
    def _log_request_end(self, status_code: int, response_time: float):
        """Log request end details"""
        try:
            response_data = {
                "request_id": getattr(g, 'request_id', None),
                "status_code": status_code,
                "response_time": response_time,
                "user_id": getattr(g.current_user, 'id', None) if hasattr(g, 'current_user') else None
            }
            
            app_logger.log_business_event("request_end", response_data)
            
        except Exception as e:
            app_logger.log_error(e, {"context": "request_end_logging"})


class SecurityMiddleware:
    """Security middleware for enhanced security headers and validations"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize security middleware"""
        app.after_request(self.add_security_headers)
    
    def add_security_headers(self, response):
        """Add security headers to response"""
        # CORS headers (should be configured properly for production)
        response.headers['Access-Control-Allow-Origin'] = '*'  # Configure for production
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy (basic)
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        
        return response


class RateLimitMiddleware:
    """Basic rate limiting middleware"""
    
    def __init__(self, app: Flask = None, requests_per_minute: int = 60):
        self.app = app
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}  # In production, use Redis
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize rate limiting middleware"""
        app.before_request(self.check_rate_limit)
    
    def check_rate_limit(self):
        """Check if request exceeds rate limit"""
        # Basic implementation - in production use Redis with sliding window
        client_ip = request.remote_addr
        current_minute = datetime.utcnow().strftime('%Y-%m-%d:%H:%M')
        key = f"{client_ip}:{current_minute}"
        
        if key not in self.request_counts:
            self.request_counts[key] = 0
        
        self.request_counts[key] += 1
        
        if self.request_counts[key] > self.requests_per_minute:
            from app.utils.response_helper import APIResponse
            return APIResponse.error(
                message="Rate limit exceeded",
                status_code=429,
                error_code="RATE_LIMIT_EXCEEDED"
            )
        
        # Clean up old entries (basic cleanup)
        self._cleanup_old_entries()
    
    def _cleanup_old_entries(self):
        """Clean up old rate limit entries"""
        current_time = datetime.utcnow()
        cutoff_time = current_time.replace(second=0, microsecond=0)
        cutoff_str = cutoff_time.strftime('%Y-%m-%d:%H:%M')
        
        keys_to_remove = []
        for key in self.request_counts:
            if key.split(':')[-1] < cutoff_str:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.request_counts[key]
