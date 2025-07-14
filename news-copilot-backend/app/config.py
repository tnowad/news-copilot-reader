import os
from typing import Dict, Any
from datetime import timedelta


class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get('JWT_ACCESS_TOKEN_HOURS', 1)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.environ.get('JWT_REFRESH_TOKEN_DAYS', 30)))
    JWT_ALGORITHM = 'HS256'
    
    # Mail Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'news-copilot-reader@example.com')
    
    # Cache Configuration
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 3600))
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # API Configuration
    API_TITLE = "News Copilot Reader API"
    API_VERSION = "v1"
    API_DESCRIPTION = "Enhanced News Reader API with AI capabilities"
    
    # Security Configuration
    BCRYPT_LOG_ROUNDS = int(os.environ.get('BCRYPT_LOG_ROUNDS', 12))
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'true').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '1000 per hour')
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # AI/ML Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    HUGGING_FACE_API_KEY = os.environ.get('HUGGING_FACE_API_KEY')
    
    # Recommendation System
    RECOMMENDATION_CACHE_TTL = int(os.environ.get('RECOMMENDATION_CACHE_TTL', 3600))
    RECOMMENDATION_BATCH_SIZE = int(os.environ.get('RECOMMENDATION_BATCH_SIZE', 50))
    
    # Monitoring
    ENABLE_METRICS = os.environ.get('ENABLE_METRICS', 'true').lower() == 'true'
    METRICS_PORT = int(os.environ.get('METRICS_PORT', 9090))
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        config = {}
        for key in dir(cls):
            if not key.startswith('_') and not callable(getattr(cls, key)):
                config[key] = getattr(cls, key)
        return config


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    
    # Development specific settings
    SQLALCHEMY_ECHO = True
    
    # Relaxed security for development
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False
    
    # Development mail settings (use MailHog or similar)
    MAIL_PORT = 1025
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = False
    TESTING = True
    
    # Use in-memory database for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable JWT expiration for tests
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Disable mail sending in tests
    MAIL_SUPPRESS_SEND = True
    
    # Use simple cache for tests
    CACHE_TYPE = 'simple'
    
    # Faster password hashing for tests
    BCRYPT_LOG_ROUNDS = 4


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Production security settings
    SESSION_COOKIE_SECURE = True
    
    # Production database settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'max_overflow': 20
    }
    
    # Production cache settings (Redis recommended)
    CACHE_TYPE = 'redis'
    
    # Production logging
    LOG_LEVEL = 'WARNING'
    
    # Enhanced security
    BCRYPT_LOG_ROUNDS = 15


class ConfigManager:
    """Configuration manager utility"""
    
    _configs = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig,
        'default': DevelopmentConfig
    }
    
    @classmethod
    def get_config(cls, env: str = None) -> Config:
        """Get configuration for environment"""
        if env is None:
            env = os.environ.get('FLASK_ENV', 'default')
        
        return cls._configs.get(env, cls._configs['default'])
    
    @classmethod
    def validate_config(cls, config: Config) -> Dict[str, str]:
        """Validate configuration and return any errors"""
        errors = []
        
        # Check required environment variables for production
        if isinstance(config, ProductionConfig):
            required_vars = [
                'SECRET_KEY',
                'JWT_SECRET_KEY',
                'DATABASE_URL',
            ]
            
            for var in required_vars:
                if not os.environ.get(var):
                    errors.append(f"Required environment variable {var} is not set")
        
        # Validate database URL format
        db_url = config.SQLALCHEMY_DATABASE_URI
        if not db_url or not db_url.startswith(('sqlite://', 'postgresql://', 'mysql://')):
            errors.append("Invalid database URL format")
        
        # Validate JWT expiration times
        if config.JWT_ACCESS_TOKEN_EXPIRES.total_seconds() <= 0:
            errors.append("JWT access token expiration must be positive")
        
        return errors
    
    @classmethod
    def print_config_summary(cls, config: Config):
        """Print configuration summary for debugging"""
        print("=== Configuration Summary ===")
        print(f"Environment: {config.__class__.__name__}")
        print(f"Debug: {getattr(config, 'DEBUG', False)}")
        print(f"Testing: {getattr(config, 'TESTING', False)}")
        print(f"Database: {config.SQLALCHEMY_DATABASE_URI}")
        print(f"Cache Type: {config.CACHE_TYPE}")
        print(f"JWT Access Token Expires: {config.JWT_ACCESS_TOKEN_EXPIRES}")
        print(f"Max Content Length: {config.MAX_CONTENT_LENGTH}")
        print("=" * 30)


# Environment-specific configurations
def get_config_for_environment():
    """Get configuration based on current environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    return ConfigManager.get_config(env)
