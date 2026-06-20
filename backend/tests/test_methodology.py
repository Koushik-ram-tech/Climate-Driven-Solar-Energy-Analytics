"""
backend/tests/test_methodology.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tests for GET /methodology.

Verifies:
  - HTTP 200 response
  - All three MethodologyResponse fields present
  - No extra fields (extra="forbid" on schema)
  - Field values match the static strings defined in methodology_service.py
  - Response is idempotent across multiple calls
"""

from __future__ import annotations

# Static values sourced from methodology_service.py — these are the
# frozen project constants that the endpoint must return exactly.
EXPECTED_TITLE = "AI-Powered Residential Solar Investment Advisor"
EXPECTED_VERSION = "1.0"


class TestMethodology:
    """Tests for GET /methodology."""

    def test_returns_200(self, client):
        response = client.get("/methodology")
        assert response.status_code == 200

    def test_content_type_is_json(self, client):
        response = client.get("/methodology")
        assert "application/json" in response.headers["content-type"]

    def test_response_contains_exactly_three_fields(self, client):
        data = client.get("/methodology").json()
        assert set(data.keys()) == {"title", "description", "version"}, (
            f"Unexpected fields: {set(data.keys())}"
        )

    def test_title_is_correct(self, client):
        data = client.get("/methodology").json()
        assert data["title"] == EXPECTED_TITLE

    def test_description_is_non_empty(self, client):
        data = client.get("/methodology").json()
        assert isinstance(data["description"], str)
        assert len(data["description"]) > 20

    def test_description_references_xgboost(self, client):
        """Description must reference the model used in the dissertation."""
        data = client.get("/methodology").json()
        assert "XGBoost" in data["description"]

    def test_version_is_correct(self, client):
        data = client.get("/methodology").json()
        assert data["version"] == EXPECTED_VERSION

    def test_no_extra_research_metrics_exposed(self, client):
        """Schema must not expose raw notebook metrics as API fields."""
        data = client.get("/methodology").json()
        forbidden = {"model_r2", "model_rmse", "cities_count",
                     "date_range_start", "date_range_end", "dataset_source"}
        present = forbidden & set(data.keys())
        assert not present, f"Unexpected metric fields exposed: {present}"

    def test_response_is_idempotent(self, client):
        """Multiple calls return the same response."""
        r1 = client.get("/methodology").json()
        r2 = client.get("/methodology").json()
        assert r1 == r2
