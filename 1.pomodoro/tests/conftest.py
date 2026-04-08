"""Pytest configuration and shared fixtures."""

import pytest
from pomodoro import create_app


@pytest.fixture
def app():
    """Create and configure an application fixture for testing."""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Create a test client fixture."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a CLI runner fixture for command testing."""
    return app.test_cli_runner()
