"""Integration tests for the Pomodoro application."""

import pytest


class TestApplicationIntegration:
    """Integration tests for application components working together."""

    def test_app_serves_index_via_root(self, client):
        """Test that the app serves HTML at root path."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.content_type

    def test_app_serves_api_health_check(self, client):
        """Test that the app serves API health check."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.is_json
        assert response.get_json()["status"] == "ok"

    def test_web_and_api_are_separate(self, client):
        """Test that web and API routes are properly separated."""
        web_response = client.get("/")
        api_response = client.get("/api/health")

        assert web_response.content_type != api_response.content_type
        assert "text/html" in web_response.content_type
        assert "application/json" in api_response.content_type

    def test_404_pages_are_consistent(self, client):
        """Test that 404 errors are handled consistently."""
        responses = [
            client.get("/invalid"),
            client.get("/api/invalid"),
            client.get("/nonexistent/path"),
        ]
        assert all(r.status_code == 404 for r in responses)

    def test_app_handles_multiple_requests(self, client):
        """Test that app handles multiple sequential requests."""
        for _ in range(5):
            response_web = client.get("/")
            response_api = client.get("/api/health")
            assert response_web.status_code == 200
            assert response_api.status_code == 200

    def test_testing_mode_configuration(self, app):
        """Test that app in testing mode has correct configuration."""
        assert app.config["TESTING"] is True
        # In testing mode, propagate_exceptions should be True by default
        # or configurable

    def test_app_static_files_accessible(self, client):
        """Test that static file routes are registered."""
        # Verify that static files can be accessed programmatically
        # (Note: actual file existence depends on Flask's static file handling)
        response = client.get("/static/css/app.css")
        assert response.status_code in [200, 304]  # 200 or 304 (cached) are ok

    def test_app_templates_directory_configured(self, app):
        """Test that templates directory is properly configured."""
        # Check that template folder is set up
        assert app.template_folder is not None
