import os
import logging
from datetime import timedelta

from flask import Flask
from flask_migrate import Migrate

from app.extensions import cache, db, jwt, mail
from app.seed import seed_database
from app.config import ConfigManager
from app.utils.error_handler import ErrorHandler
from app.utils.logging import app_logger
from app.middleware.request_middleware import RequestMiddleware, SecurityMiddleware

migrate = Migrate()


def create_app(config_name: str = None):
    """Enhanced application factory with comprehensive configuration"""
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    config_class = ConfigManager.get_config(config_name)
    app.config.from_object(config_class)
    
    # Validate configuration
    config_errors = ConfigManager.validate_config(config_class)
    if config_errors:
        app_logger.log_error(Exception("Configuration validation failed"), {
            "errors": config_errors
        })
        if config_name == 'production':
            raise Exception("Configuration validation failed in production")
    
    # Print configuration summary in development
    if config_name == 'development':
        ConfigManager.print_config_summary(config_class)
    
    # Initialize extensions
    _initialize_extensions(app)
    
    # Register error handlers
    ErrorHandler.register_error_handlers(app)
    
    # Initialize middleware
    _initialize_middleware(app)
    
    # Setup logging
    _setup_logging(app)
    
    # Register blueprints and initialize database
    with app.app_context():
        _register_blueprints(app)
        _initialize_database(app)
    
    app_logger.log_business_event("app_startup", {
        "config": config_name,
        "debug": app.debug,
        "testing": app.testing
    })
    
    return app


def _initialize_extensions(app: Flask):
    """Initialize Flask extensions"""
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    cache.init_app(app)
    mail.init_app(app)
    
    # Configure JWT additional settings
    @jwt.additional_claims_loader
    def add_claims_to_access_token(identity):
        # Add additional claims to JWT token
        from app.models.user import User
        user = User.query.filter_by(email=identity).first()
        if user:
            return {
                "user_id": user.id,
                "roles": [str(role.name) for role in user.roles]
            }
        return {}
    
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.email if hasattr(user, 'email') else user
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        from app.models.user import User
        return User.query.filter_by(email=identity).one_or_none()


def _initialize_middleware(app: Flask):
    """Initialize application middleware"""
    RequestMiddleware(app)
    SecurityMiddleware(app)


def _setup_logging(app: Flask):
    """Setup application logging"""
    # Configure logging level
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    logging.basicConfig(
        level=log_level,
        format=app.config.get('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # Add file handler for production
    if not app.debug and not app.testing:
        import logging.handlers
        
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Setup rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            'logs/app.log', maxBytes=10240000, backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app_logger.log_business_event("logging_configured", {
            "log_level": app.config.get('LOG_LEVEL', 'INFO'),
            "file_logging": True
        })


def _register_blueprints(app: Flask):
    """Register application blueprints"""
    from .routes import routes_bp
    app.register_blueprint(routes_bp)
    
    # Register health check endpoint
    @app.route('/health')
    def health_check():
        from app.utils.database_utils import DatabaseHealthCheck
        from app.utils.response_helper import APIResponse
        
        db_health = DatabaseHealthCheck.check_connection()
        
        if db_health['status'] == 'healthy':
            return APIResponse.success(
                message="Application is healthy",
                data={
                    "status": "healthy",
                    "database": db_health,
                    "timestamp": db_health['timestamp']
                }
            )
        else:
            return APIResponse.error(
                message="Application is unhealthy",
                error_details=db_health,
                status_code=503
            )
    
    # Register metrics endpoint
    @app.route('/metrics')
    def metrics():
        from app.utils.logging import performance_monitor
        from app.utils.response_helper import APIResponse
        
        metrics_data = performance_monitor.get_metrics()
        return APIResponse.success(
            message="Application metrics",
            data=metrics_data
        )


def _initialize_database(app: Flask):
    """Initialize database and seed data"""
    try:
        db.create_all()
        seed_database()
        
        app_logger.log_business_event("database_initialized", {
            "database_uri": app.config.get('SQLALCHEMY_DATABASE_URI', '').split('://')[0],
            "seeded": True
        })
        
    except Exception as e:
        app_logger.log_error(e, {"context": "database_initialization"})
        raise

        app.register_blueprint(routes_bp)

        return app
