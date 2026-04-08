"""Tests for web routes (HTML pages)."""

import pytest


class TestWebRoutes:
    """Test web page routes."""

    def test_index_route_exists(self, client):
        """Test that GET / returns a successful response."""
        response = client.get("/")
        assert response.status_code == 200

    def test_index_returns_html_content_type(self, client):
        """Test that index route returns HTML content type."""
        response = client.get("/")
        assert "text/html" in response.content_type

    def test_index_renders_template(self, client):
        """Test that index route renders the index.html template."""
        response = client.get("/")
        assert b"Pomodoro Timer" in response.data

    def test_index_contains_bootstrap_message(self, client):
        """Test that bootstrap page contains expected content."""
        response = client.get("/")
        assert b"Step 1 bootstrap complete" in response.data or b"Pomodoro" in response.data

    def test_index_contains_main_element(self, client):
        """Test that index page contains main element."""
        response = client.get("/")
        assert b"<main" in response.data

    def test_index_includes_static_css(self, client):
        """Test that index page references CSS files."""
        response = client.get("/")
        # Check for link to tokens.css or app.css
        assert b"css" in response.data

    def test_index_includes_static_js(self, client):
        """Test that index page references JavaScript files."""
        response = client.get("/")
        assert b"js" in response.data or b"script" in response.data

    def test_invalid_route_returns_404(self, client):
        """Test that invalid routes return 404."""
        response = client.get("/invalid-route-that-does-not-exist")
        assert response.status_code == 404

    def test_index_route_methods(self, client):
        """Test that index route only accepts GET."""
        response = client.post("/")
        assert response.status_code == 405  # Method Not Allowed

    def test_index_response_is_not_empty(self, client):
        """Test that index response contains content."""
        response = client.get("/")
        assert len(response.data) > 0
