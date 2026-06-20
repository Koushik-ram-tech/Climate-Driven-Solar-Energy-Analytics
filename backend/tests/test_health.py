"""
backend/tests/test_health.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tests for GET /health.

Verifies:
  - HTTP 200 response
  - Response body matches HealthResponse schema
  - status field equals "healthy" (the only valid Literal value)
  - Response contains no extra fields
  - Content-Type is application/json
"""

from __future__ import annotations


class TestHealth:
    """Tests for GET /health."""

    def test_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_content_type_is_json(self, client):
        response = client.get("/health")
        assert "application/json" in response.headers["content-type"]

    def test_status_is_healthy(self, client):
        data = client.get("/health").json()
        assert data["status"] == "healthy"

    def test_response_contains_only_status_field(self, client):
        data = client.get("/health").json()
        assert set(data.keys()) == {"status"}

    def test_response_is_idempotent(self, client):
        """Multiple calls return the same response."""
        r1 = client.get("/health").json()
        r2 = client.get("/health").json()
        assert r1 == r2
