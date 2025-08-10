import pytest
from app.config import Config, DevelopmentConfig, TestingConfig, ProductionConfig, ConfigManager


class TestConfig:
    def test_base_config(self):
        config = Config()

        assert config.SECRET_KEY is not None
        assert config.SQLALCHEMY_TRACK_MODIFICATIONS is False
        assert config.JWT_ALGORITHM == "HS256"

    def test_development_config(self):
        config = DevelopmentConfig()

        assert config.DEBUG is True
        assert config.SQLALCHEMY_ECHO is True
        assert config.SESSION_COOKIE_SECURE is False

    def test_testing_config(self):
        config = TestingConfig()

        assert config.TESTING is True
        assert config.SQLALCHEMY_DATABASE_URI == "sqlite:///:memory:"
        assert config.BCRYPT_LOG_ROUNDS == 4

    def test_production_config(self):
        config = ProductionConfig()

        assert config.DEBUG is False
        assert config.SESSION_COOKIE_SECURE is True
        assert config.LOG_LEVEL == "WARNING"

    def test_config_manager_default(self):
        config_class = ConfigManager.get_config("default")
        assert config_class is DevelopmentConfig

    def test_config_manager_development(self):
        config_class = ConfigManager.get_config("development")
        assert config_class is DevelopmentConfig

    def test_config_manager_testing(self):
        config_class = ConfigManager.get_config("testing")
        assert config_class is TestingConfig

    def test_config_manager_production(self):
        config_class = ConfigManager.get_config("production")
        assert config_class is ProductionConfig

    def test_config_manager_invalid_env(self):
        config_class = ConfigManager.get_config("nonexistent")
        assert config_class is DevelopmentConfig

    def test_config_dict(self):
        config = TestingConfig()
        config_dict = config.get_config_dict()

        assert "TESTING" in config_dict
        assert config_dict["TESTING"] is True

    def test_config_validation(self):
        config = TestingConfig()
        errors = ConfigManager.validate_config(config)

        assert isinstance(errors, list)

    def test_config_validation_production_missing_vars(self, monkeypatch):
        monkeypatch.delenv("SECRET_KEY", raising=False)
        monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
        monkeypatch.delenv("DATABASE_URL", raising=False)

        config = ProductionConfig()
        errors = ConfigManager.validate_config(config)

        assert len(errors) > 0
