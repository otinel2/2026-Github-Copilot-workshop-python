"""Tests for API routes."""

import pytest
import json


class TestAPIRoutes:
    """Test API routes."""

    def test_health_route_exists(self, client):
        """Test that GET /api/health returns a successful response."""
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_returns_json_content_type(self, client):
        """Test that health route returns JSON content type."""
        response = client.get("/api/health")
        assert "application/json" in response.content_type

    def test_health_response_structure(self, client):
        """Test that health response has expected JSON structure."""
        response = client.get("/api/health")
        data = response.get_json()
        assert isinstance(data, dict)
        assert "status" in data

    def test_health_response_ok_status(self, client):
        """Test that health endpoint returns 'ok' status."""
        response = client.get("/api/health")
        data = response.get_json()
        assert data["status"] == "ok"

    def test_health_response_is_valid_json(self, client):
        """Test that health response is valid JSON."""
        response = client.get("/api/health")
        assert response.is_json
        assert response.get_json() is not None

    def test_health_route_methods(self, client):
        """Test that health route only accepts GET."""
        response = client.post("/api/health")
        assert response.status_code == 405  # Method Not Allowed

    def test_api_route_prefix(self, client):
        """Test that API routes are under /api prefix."""
        response = client.get("/api/health")
        assert response.status_code == 200
        # Non-prefixed version should not exist
        response = client.get("/health")
        assert response.status_code == 404

    def test_invalid_api_route_returns_404(self, client):
        """Test that invalid API routes return 404."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_health_endpoint_reliability(self, client):
        """Test that health endpoint is reliable across multiple calls."""
        responses = [client.get("/api/health") for _ in range(3)]
        assert all(r.status_code == 200 for r in responses)
        assert all(r.get_json()["status"] == "ok" for r in responses)
