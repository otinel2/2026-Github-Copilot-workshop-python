"""Tests for application configuration."""

import os
import pytest
from pomodoro.config import Config


class TestConfig:
    """Test configuration module."""

    def test_config_secret_key_default(self):
        """Test that Config has default SECRET_KEY."""
        config = Config()
        assert hasattr(config, "SECRET_KEY")
        assert config.SECRET_KEY is not None

    def test_config_secret_key_from_env(self, monkeypatch):
        """Test that Config respects SECRET_KEY environment variable."""
        monkeypatch.setenv("SECRET_KEY", "env-secret-key")
        # Re-import to get the env variable
        from importlib import reload
        import pomodoro.config

        reload(pomodoro.config)
        config = pomodoro.config.Config()
        assert config.SECRET_KEY == "env-secret-key"

    def test_config_secret_key_fallback(self, monkeypatch):
        """Test that Config falls back to dev key when env var not set."""
        monkeypatch.delenv("SECRET_KEY", raising=False)
        config = Config()
        assert config.SECRET_KEY == "dev-secret-key"
