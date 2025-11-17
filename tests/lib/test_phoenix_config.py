"""Tests for Universal Configuration."""

import pytest
import tempfile
import yaml
from pathlib import Path

from phoenix_config import (
    UniversalConfig,
    DatabaseConfig,
    APIConfig,
    LoggingConfig,
    ConfigurationError,
)


class TestUniversalConfig:
    def test_default_config(self):
        """Test creating default configuration."""
        config = UniversalConfig.create_default()

        assert config.environment == "production"
        assert config.database.url == "sqlite:///app.db"
        assert config.api.host == "localhost"
        assert config.api.port == 8000
        assert config.logging.level == "INFO"

    def test_production_config(self):
        """Test creating production configuration."""
        config = UniversalConfig.create_for_production()

        assert config.environment == "production"
        assert config.api.debug is False
        assert config.api.workers >= 1
        assert config.logging.level == "INFO"
        assert config.performance.enable_caching is True

    def test_development_config(self):
        """Test creating development configuration."""
        project_root = Path("/tmp/test")
        config = UniversalConfig.create_for_development(project_root)

        assert config.environment == "development"
        assert config.project_root == project_root
        assert config.api.debug is True
        assert config.database.echo is True
        assert config.logging.level == "DEBUG"
        assert config.logging.format == "console"

    def test_testing_config(self):
        """Test creating testing configuration."""
        config = UniversalConfig.create_for_testing()

        assert config.environment == "test"
        assert config.database.url == "sqlite:///:memory:"
        assert config.performance.enable_caching is False
        assert config.logging.level == "WARNING"

    def test_testing_config_with_overrides(self):
        """Test creating testing configuration with overrides."""
        config = UniversalConfig.create_for_testing(
            database=DatabaseConfig(url="postgresql://test"), logging=LoggingConfig(level="DEBUG")
        )

        assert config.environment == "test"
        assert config.database.url == "postgresql://test"
        assert config.logging.level == "DEBUG"

    def test_environment_detection(self):
        """Test environment detection methods."""
        prod_config = UniversalConfig.create_for_production()
        dev_config = UniversalConfig.create_for_development(Path.cwd())
        test_config = UniversalConfig.create_for_testing()

        assert prod_config.is_production()
        assert not prod_config.is_development()
        assert not prod_config.is_test()

        assert dev_config.is_development()
        assert not dev_config.is_production()
        assert not dev_config.is_test()

        assert test_config.is_test()
        assert not test_config.is_production()
        assert not test_config.is_development()

    def test_validation_errors(self):
        """Test configuration validation."""
        with pytest.raises(ConfigurationError) as exc_info:
            UniversalConfig(
                environment="invalid",
                database=DatabaseConfig(pool_size=-1),
                api=APIConfig(port=99999),
            )

        errors = exc_info.value.validation_errors
        assert len(errors) >= 3
        assert any("environment must be one of" in error for error in errors)
        assert any("pool_size must be positive" in error for error in errors)
        assert any("port must be between" in error for error in errors)

    def test_to_dict(self):
        """Test converting configuration to dictionary."""
        config = UniversalConfig.create_default()
        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert "environment" in config_dict
        assert "database" in config_dict
        assert "api" in config_dict
        assert config_dict["environment"] == "production"

    def test_save_and_load_file(self):
        """Test saving and loading configuration from file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.yaml"

            # Create and save config
            original_config = UniversalConfig.create_for_development(Path(temp_dir))
            original_config.save_to_file(config_path)

            # Verify file exists and has correct content
            assert config_path.exists()

            with open(config_path) as f:
                data = yaml.safe_load(f)
            assert data["environment"] == "development"

            # Load config from file
            loaded_config = UniversalConfig.load_from_file(config_path)
            assert loaded_config.environment == original_config.environment
            assert loaded_config.api.debug == original_config.api.debug

    def test_load_from_env(self):
        """Test loading configuration from environment variables."""
        import os

        # Set environment variables
        env_vars = {
            "APP_ENV": "test",
            "DATABASE_URL": "postgresql://test",
            "API_PORT": "9000",
            "DEBUG": "true",
            "LOG_LEVEL": "DEBUG",
        }

        # Backup original env vars
        original_env = {}
        for key, value in env_vars.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value

        try:
            config = UniversalConfig.load_from_env()

            assert config.environment == "test"
            assert config.database.url == "postgresql://test"
            assert config.api.port == 9000
            assert config.api.debug is True
            assert config.logging.level == "DEBUG"
        finally:
            # Restore original env vars
            for key, original_value in original_env.items():
                if original_value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = original_value

    def test_get_database_url(self):
        """Test getting database URL with environment substitution."""
        config = UniversalConfig(database=DatabaseConfig(url="postgresql://${USER}@localhost/db"))

        # Should substitute ${USER} if available
        url = config.get_database_url()
        assert "postgresql://" in url
        assert "@localhost/db" in url

    def test_custom_configuration(self):
        """Test creating custom configuration."""
        config = UniversalConfig(
            environment="production",
            database=DatabaseConfig(
                url="postgresql://user:pass@localhost/prod", pool_size=20, echo=False
            ),
            api=APIConfig(host="0.0.0.0", port=80, workers=8, debug=False),
            logging=LoggingConfig(level="INFO", format="json", log_file="/var/log/app.log"),
        )

        config.validate()  # Should not raise

        assert config.database.pool_size == 20
        assert config.api.host == "0.0.0.0"
        assert config.api.workers == 8
        assert config.logging.format == "json"
        assert config.logging.log_file == "/var/log/app.log"


class TestComponentConfigs:
    def test_database_config_defaults(self):
        """Test DatabaseConfig defaults."""
        config = DatabaseConfig()
        assert config.url == "sqlite:///app.db"
        assert config.echo is False
        assert config.pool_size == 5
        assert config.auto_create_tables is True

    def test_api_config_defaults(self):
        """Test APIConfig defaults."""
        config = APIConfig()
        assert config.host == "localhost"
        assert config.port == 8000
        assert config.debug is False
        assert config.workers == 1

    def test_logging_config_defaults(self):
        """Test LoggingConfig defaults."""
        config = LoggingConfig()
        assert config.level == "INFO"
        assert config.format == "json"
        assert config.include_timestamp is True
        assert config.log_file is None
