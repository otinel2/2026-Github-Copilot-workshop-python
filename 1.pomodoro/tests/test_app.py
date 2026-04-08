"""Tests for application factory and initialization."""

import pytest
from pomodoro import create_app
from pomodoro.config import Config


class TestCreateApp:
    """Test application factory."""

    def test_create_app_returns_flask_instance(self):
        """Test that create_app returns a Flask instance."""
        app = create_app()
        assert app is not None
        assert hasattr(app, "config")
        assert hasattr(app, "register_blueprint")

    def test_create_app_with_custom_config(self):
        """Test that create_app accepts custom config class."""

        class CustomConfig(Config):
            SECRET_KEY = "custom-secret"

        app = create_app(config_class=CustomConfig)
        assert app.config["SECRET_KEY"] == "custom-secret"

    def test_app_has_required_blueprints(self, app):
        """Test that app registers all required blueprints."""
        blueprints = app.blueprints
        assert "web" in blueprints
        assert "api" in blueprints

    def test_app_config_contains_secret_key(self, app):
        """Test that app config contains SECRET_KEY."""
        assert "SECRET_KEY" in app.config
        assert app.config["SECRET_KEY"] is not None

    def test_app_testing_mode(self, app):
        """Test that app can be configured for testing."""
        assert app.config["TESTING"] is True

    def test_api_blueprint_has_url_prefix(self, app):
        """Test that API blueprint is registered with /api prefix."""
        # Verify by checking a known API route
        health_route = None
        for rule in app.url_map.iter_rules():
            if rule.endpoint == "api.health":
                health_route = str(rule)
                break
        assert health_route is not None
        assert "/api/health" in health_route
