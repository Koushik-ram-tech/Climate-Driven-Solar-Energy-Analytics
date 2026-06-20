"""
backend/tests/test_readiness.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tests for GET /readiness/{city}.

Verifies:
  - HTTP 200 for valid city name and slug
  - HTTP 404 for unsupported city
  - All ReadinessResponse fields are present
  - Field values are within observed CSV ranges
  - Categorical fields (suitability, prediction_confidence, rs_category)
    contain only valid values
  - Suitability is clean (no emoji prefix)
  - Slug lookup and canonical name lookup both work
  - All 15 cities return valid responses
"""

from __future__ import annotations

import pytest


# Valid categorical values sourced directly from sdsf_city_dashboard.csv
VALID_SUITABILITY: frozenset[str] = frozenset(
    {"Highly Suitable", "Suitable", "Moderately Suitable"}
)
VALID_PREDICTION_CONFIDENCE: frozenset[str] = frozenset({"High", "Medium", "Low"})
VALID_RS_CATEGORY: frozenset[str] = frozenset(
    {"Consistent Producer", "Seasonal Producer"}
)

# All 15 (name, slug) pairs for parametrised tests
ALL_CITIES: list[tuple[str, str]] = [
    ("Ahmedabad",   "ahmedabad"),
    ("Bengaluru",   "bengaluru"),
    ("Bhopal",      "bhopal"),
    ("Bhubaneswar", "bhubaneswar"),
    ("Chandigarh",  "chandigarh"),
    ("Chennai",     "chennai"),
    ("Delhi",       "delhi"),
    ("Guwahati",    "guwahati"),
    ("Hyderabad",   "hyderabad"),
    ("Jaipur",      "jaipur"),
    ("Kochi",       "kochi"),
    ("Kolkata",     "kolkata"),
    ("Mangalore",   "mangalore"),
    ("Mumbai",      "mumbai"),
    ("Pune",        "pune"),
]

# ReadinessResponse required fields (all 13 — verified against readiness_response.py)
REQUIRED_FIELDS: set[str] = {
    "city", "city_slug", "mean_ghi",
    "p10_ghi", "p50_ghi", "p90_ghi",
    "reliability_score", "rs_category",
    "model_rmse", "model_mape",
    "prediction_confidence", "suitability", "explanation",
}


class TestReadinessValid:
    """Valid city requests — HTTP 200 and correct response shape."""

    def test_canonical_name_returns_200(self, client):
        response = client.get("/readiness/Bengaluru")
        assert response.status_code == 200

    def test_slug_returns_200(self, client):
        response = client.get("/readiness/bengaluru")
        assert response.status_code == 200

    def test_slug_and_name_return_identical_data(self, client):
        by_name = client.get("/readiness/Bengaluru").json()
        by_slug = client.get("/readiness/bengaluru").json()
        assert by_name == by_slug

    def test_response_contains_all_required_fields(self, client):
        data = client.get("/readiness/Bengaluru").json()
        missing = REQUIRED_FIELDS - set(data.keys())
        assert not missing, f"Missing fields: {missing}"

    def test_response_contains_no_extra_forbidden_fields(self, client):
        data = client.get("/readiness/Bengaluru").json()
        forbidden = {"suitability_raw", "payback_years", "annual_savings",
                     "system_size_kw", "top_shap_feature", "investment_recommendation"}
        present = forbidden & set(data.keys())
        assert not present, f"Forbidden fields present: {present}"

    def test_city_field_matches_canonical_name(self, client):
        data = client.get("/readiness/bengaluru").json()
        assert data["city"] == "Bengaluru"

    def test_city_slug_field_is_correct(self, client):
        data = client.get("/readiness/Bengaluru").json()
        assert data["city_slug"] == "bengaluru"


class TestReadinessFieldValues:
    """Field value assertions for Bengaluru (known CSV values)."""

    @pytest.fixture(autouse=True)
    def bengaluru_data(self, client):
        self._data = client.get("/readiness/Bengaluru").json()

    def test_mean_ghi_matches_csv(self):
        assert abs(self._data["mean_ghi"] - 5.272) < 0.001

    def test_p10_ghi_matches_csv(self):
        assert abs(self._data["p10_ghi"] - 3.58) < 0.001

    def test_p50_ghi_matches_csv(self):
        assert abs(self._data["p50_ghi"] - 5.37) < 0.001

    def test_p90_ghi_matches_csv(self):
        assert abs(self._data["p90_ghi"] - 6.88) < 0.001

    def test_reliability_score_matches_csv(self):
        assert abs(self._data["reliability_score"] - 81.1) < 0.1

    def test_rs_category_matches_csv(self):
        assert self._data["rs_category"] == "Consistent Producer"

    def test_model_rmse_is_positive(self):
        assert self._data["model_rmse"] > 0

    def test_model_mape_is_positive(self):
        assert self._data["model_mape"] > 0

    def test_prediction_confidence_matches_csv(self):
        assert self._data["prediction_confidence"] == "High"

    def test_suitability_matches_csv_clean(self):
        assert self._data["suitability"] == "Highly Suitable"

    def test_suitability_contains_no_emoji(self):
        suit = self._data["suitability"]
        assert "✅" not in suit
        assert "👍" not in suit
        assert "⚠️" not in suit

    def test_explanation_is_non_empty_string(self):
        assert isinstance(self._data["explanation"], str)
        assert len(self._data["explanation"]) > 20

    def test_ghi_percentile_ordering(self):
        """P10 ≤ mean_ghi ≤ P90 for Bengaluru."""
        assert self._data["p10_ghi"] < self._data["mean_ghi"] < self._data["p90_ghi"]


class TestReadinessCategoricals:
    """All categorical values across all 15 cities are within valid sets."""

    @pytest.mark.parametrize("city_name,city_slug", ALL_CITIES)
    def test_suitability_is_valid(self, client, city_name, city_slug):
        data = client.get(f"/readiness/{city_slug}").json()
        assert data["suitability"] in VALID_SUITABILITY, (
            f"{city_name}: invalid suitability {data['suitability']!r}"
        )

    @pytest.mark.parametrize("city_name,city_slug", ALL_CITIES)
    def test_prediction_confidence_is_valid(self, client, city_name, city_slug):
        data = client.get(f"/readiness/{city_slug}").json()
        assert data["prediction_confidence"] in VALID_PREDICTION_CONFIDENCE, (
            f"{city_name}: invalid confidence {data['prediction_confidence']!r}"
        )

    @pytest.mark.parametrize("city_name,city_slug", ALL_CITIES)
    def test_rs_category_is_valid(self, client, city_name, city_slug):
        data = client.get(f"/readiness/{city_slug}").json()
        assert data["rs_category"] in VALID_RS_CATEGORY, (
            f"{city_name}: invalid rs_category {data['rs_category']!r}"
        )


class TestReadinessAllCities:
    """Every city returns HTTP 200 with a complete response."""

    @pytest.mark.parametrize("city_name,city_slug", ALL_CITIES)
    def test_all_cities_return_200_by_slug(self, client, city_name, city_slug):
        response = client.get(f"/readiness/{city_slug}")
        assert response.status_code == 200, (
            f"{city_name}: expected 200, got {response.status_code}"
        )

    @pytest.mark.parametrize("city_name,city_slug", ALL_CITIES)
    def test_all_cities_have_positive_mean_ghi(self, client, city_name, city_slug):
        data = client.get(f"/readiness/{city_slug}").json()
        assert data["mean_ghi"] > 0

    @pytest.mark.parametrize("city_name,city_slug", ALL_CITIES)
    def test_all_cities_city_field_matches_name(self, client, city_name, city_slug):
        data = client.get(f"/readiness/{city_slug}").json()
        assert data["city"] == city_name


class TestReadinessInvalidCity:
    """Unsupported or malformed city values return HTTP 404."""

    @pytest.mark.parametrize("city", [
        "varanasi",
        "Varanasi",
        "bengalooru",
        "BENGALURU",
        "london",
        "xyz",
        "123",
    ])
    def test_unsupported_city_returns_404(self, client, city):
        response = client.get(f"/readiness/{city}")
        assert response.status_code == 404, (
            f"Expected 404 for {city!r}, got {response.status_code}"
        )

    def test_404_response_has_detail_field(self, client):
        response = client.get("/readiness/varanasi")
        assert "detail" in response.json()
