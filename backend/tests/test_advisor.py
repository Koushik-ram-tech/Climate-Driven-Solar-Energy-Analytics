"""
backend/tests/test_advisor.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tests for POST /advisor.

Verifies:
  - HTTP 200 for valid requests
  - All AdvisorResponse fields present and positive where expected
  - Standard profile outputs match pre-computed CSV values (within rounding)
  - HTTP 422 for invalid field values and missing fields
  - HTTP 422 for unsupported city (rejected by Pydantic Literal)
  - Boundary inputs (min/max bill, roof, budget) return valid responses
  - MIN_SYS_KW and MAX_PHASE1_KW bounds enforced
  - Forbidden fields absent from response
  - Suitability has no emoji
  - Explanation contains city name
  - All 15 cities return valid responses
"""

from __future__ import annotations

import pytest

# Standard profile — matches the inputs used to generate the pre-computed CSV.
# Used to cross-validate the live calculation against frozen research outputs.
STANDARD_PROFILE = {
    "city": "Bengaluru",
    "monthly_bill": 3000.0,
    "roof_area_sqft": 500.0,
    "budget": 400_000.0,
}

# Known pre-computed CSV outputs for the standard profile (Bengaluru).
# Tolerance: ±1 for integers, ±0.1 for floats.
EXPECTED_BENGALURU = {
    "city":                     "Bengaluru",
    "city_slug":                "bengaluru",
    "system_size_kw":           3.0,
    "annual_generation_kwh":    4503,
    "annual_savings":           31520,
    "payback_years":            3.7,
    "lifetime_savings":         1_224_427,
    "investment_recommendation": "Highly Recommended",
    "suitability":              "Highly Suitable",
    "prediction_confidence":    "High",
}

VALID_RECOMMENDATIONS: frozenset[str] = frozenset(
    {"Highly Recommended", "Recommended", "Consider Carefully", "Not Recommended"}
)
VALID_SUITABILITY: frozenset[str] = frozenset(
    {"Highly Suitable", "Suitable", "Moderately Suitable"}
)
VALID_CONFIDENCE: frozenset[str] = frozenset({"High", "Medium", "Low"})

# All 15 supported cities
ALL_CITIES: list[str] = [
    "Ahmedabad", "Bengaluru", "Bhopal", "Bhubaneswar", "Chandigarh",
    "Chennai", "Delhi", "Guwahati", "Hyderabad", "Jaipur",
    "Kochi", "Kolkata", "Mangalore", "Mumbai", "Pune",
]

# Required AdvisorResponse fields (from advisor_response.py)
REQUIRED_FIELDS: set[str] = {
    "city", "city_slug", "system_size_kw", "annual_generation_kwh",
    "annual_savings", "payback_years", "lifetime_savings", "net_benefit_inr",
    "investment_recommendation", "recommendation_explanation",
    "suitability", "reliability_score", "prediction_confidence",
}

FORBIDDEN_FIELDS: set[str] = {
    "system_cost_gross", "subsidy", "system_cost_net",
    "suitability_raw", "limiting_factor", "limiting_message",
}


def _post(client, payload: dict) -> tuple[int, dict]:
    """Helper: POST /advisor and return (status_code, json)."""
    r = client.post("/advisor", json=payload)
    return r.status_code, r.json()


class TestAdvisorStandardProfile:
    """Standard profile cross-validates live calculation against CSV outputs."""

    @pytest.fixture(autouse=True)
    def response(self, client):
        self._status, self._data = _post(client, STANDARD_PROFILE)

    def test_returns_200(self):
        assert self._status == 200

    def test_all_required_fields_present(self):
        missing = REQUIRED_FIELDS - set(self._data.keys())
        assert not missing, f"Missing fields: {missing}"

    def test_no_forbidden_fields_present(self):
        present = FORBIDDEN_FIELDS & set(self._data.keys())
        assert not present, f"Forbidden fields present: {present}"

    def test_city_matches(self):
        assert self._data["city"] == EXPECTED_BENGALURU["city"]

    def test_city_slug_matches(self):
        assert self._data["city_slug"] == EXPECTED_BENGALURU["city_slug"]

    def test_system_size_kw_matches_csv(self):
        assert abs(self._data["system_size_kw"] - EXPECTED_BENGALURU["system_size_kw"]) <= 0.1

    def test_annual_generation_kwh_matches_csv(self):
        assert abs(self._data["annual_generation_kwh"] - EXPECTED_BENGALURU["annual_generation_kwh"]) <= 1

    def test_annual_savings_matches_csv(self):
        assert abs(self._data["annual_savings"] - EXPECTED_BENGALURU["annual_savings"]) <= 1

    def test_payback_years_matches_csv(self):
        assert abs(self._data["payback_years"] - EXPECTED_BENGALURU["payback_years"]) <= 0.1

    def test_lifetime_savings_matches_csv(self):
        assert abs(self._data["lifetime_savings"] - EXPECTED_BENGALURU["lifetime_savings"]) <= 1

    def test_investment_recommendation_matches_csv(self):
        assert self._data["investment_recommendation"] == EXPECTED_BENGALURU["investment_recommendation"]

    def test_suitability_matches_csv(self):
        assert self._data["suitability"] == EXPECTED_BENGALURU["suitability"]

    def test_prediction_confidence_matches_csv(self):
        assert self._data["prediction_confidence"] == EXPECTED_BENGALURU["prediction_confidence"]


class TestAdvisorResponseQuality:
    """Semantic correctness of the advisor response."""

    @pytest.fixture(autouse=True)
    def response(self, client):
        self._data = _post(client, STANDARD_PROFILE)[1]

    def test_system_size_kw_is_positive(self):
        assert self._data["system_size_kw"] > 0

    def test_annual_generation_kwh_is_positive(self):
        assert self._data["annual_generation_kwh"] > 0

    def test_annual_savings_is_positive(self):
        assert self._data["annual_savings"] > 0

    def test_payback_years_is_positive_and_finite(self):
        pb = self._data["payback_years"]
        assert pb > 0
        assert pb < 1000  # sanity guard against float("inf") leaking

    def test_lifetime_savings_is_positive(self):
        assert self._data["lifetime_savings"] > 0

    def test_lifetime_savings_exceeds_annual_savings(self):
        assert self._data["lifetime_savings"] > self._data["annual_savings"]

    def test_net_benefit_inr_is_present(self):
        assert "net_benefit_inr" in self._data

    def test_recommendation_is_valid_value(self):
        assert self._data["investment_recommendation"] in VALID_RECOMMENDATIONS

    def test_explanation_is_non_empty_string(self):
        expl = self._data["recommendation_explanation"]
        assert isinstance(expl, str)
        assert len(expl) > 50

    def test_explanation_contains_city_name(self):
        assert "Bengaluru" in self._data["recommendation_explanation"]

    def test_suitability_is_valid_value(self):
        assert self._data["suitability"] in VALID_SUITABILITY

    def test_suitability_contains_no_emoji(self):
        suit = self._data["suitability"]
        assert "✅" not in suit
        assert "👍" not in suit
        assert "⚠️" not in suit

    def test_reliability_score_is_positive(self):
        assert self._data["reliability_score"] > 0

    def test_prediction_confidence_is_valid(self):
        assert self._data["prediction_confidence"] in VALID_CONFIDENCE


class TestAdvisorBoundaryInputs:
    """Boundary values all return HTTP 200 with valid responses."""

    def _assert_valid_response(self, client, payload: dict, label: str):
        status, data = _post(client, payload)
        assert status == 200, f"{label}: expected 200, got {status} — {data}"
        assert data["system_size_kw"] >= 1.0, f"{label}: system_size_kw < MIN_SYS_KW"
        assert data["system_size_kw"] <= 10.0, f"{label}: system_size_kw > MAX_PHASE1_KW"
        assert data["annual_generation_kwh"] > 0
        assert data["annual_savings"] > 0
        assert data["investment_recommendation"] in VALID_RECOMMENDATIONS

    def test_minimum_monthly_bill(self, client):
        self._assert_valid_response(
            client,
            {**STANDARD_PROFILE, "monthly_bill": 500.0},
            "monthly_bill=500 (minimum)",
        )

    def test_maximum_monthly_bill(self, client):
        self._assert_valid_response(
            client,
            {**STANDARD_PROFILE, "monthly_bill": 100_000.0},
            "monthly_bill=100000 (maximum)",
        )

    def test_minimum_roof_area(self, client):
        self._assert_valid_response(
            client,
            {**STANDARD_PROFILE, "roof_area_sqft": 50.0},
            "roof_area_sqft=50 (minimum)",
        )

    def test_maximum_roof_area(self, client):
        self._assert_valid_response(
            client,
            {**STANDARD_PROFILE, "roof_area_sqft": 5_000.0},
            "roof_area_sqft=5000 (maximum)",
        )

    def test_minimum_budget(self, client):
        self._assert_valid_response(
            client,
            {**STANDARD_PROFILE, "budget": 50_000.0},
            "budget=50000 (minimum)",
        )

    def test_maximum_budget(self, client):
        self._assert_valid_response(
            client,
            {**STANDARD_PROFILE, "budget": 50_00_000.0},
            "budget=5000000 (maximum)",
        )

    def test_minimum_roof_clamps_to_min_sys_kw(self, client):
        """Very small roof → system_size_kw is still >= MIN_SYS_KW (1.0 kW)."""
        _, data = _post(client, {**STANDARD_PROFILE, "roof_area_sqft": 50.0, "budget": 50_000.0})
        assert data["system_size_kw"] >= 1.0

    def test_maximum_inputs_cap_at_max_phase1_kw(self, client):
        """Maximum roof + budget + bill → system_size_kw never exceeds 10.0 kW."""
        _, data = _post(client, {
            "city": "Chennai",
            "monthly_bill": 100_000.0,
            "roof_area_sqft": 5_000.0,
            "budget": 50_00_000.0,
        })
        assert data["system_size_kw"] <= 10.0


class TestAdvisorInvalidRequests:
    """Invalid inputs return HTTP 422 (Pydantic validation)."""

    @pytest.mark.parametrize("payload,label", [
        # Missing fields
        ({"monthly_bill": 3000.0, "roof_area_sqft": 500.0, "budget": 400_000.0},
         "missing city"),
        ({"city": "Bengaluru", "roof_area_sqft": 500.0, "budget": 400_000.0},
         "missing monthly_bill"),
        ({"city": "Bengaluru", "monthly_bill": 3000.0, "budget": 400_000.0},
         "missing roof_area_sqft"),
        ({"city": "Bengaluru", "monthly_bill": 3000.0, "roof_area_sqft": 500.0},
         "missing budget"),
        # City: unsupported name (Literal rejects it before service)
        ({**STANDARD_PROFILE, "city": "Varanasi"},     "unsupported city"),
        ({**STANDARD_PROFILE, "city": "bengaluru"},    "lowercase city (case-sensitive)"),
        ({**STANDARD_PROFILE, "city": ""},             "empty city string"),
        # monthly_bill out of range
        ({**STANDARD_PROFILE, "monthly_bill": 499.99}, "bill below minimum"),
        ({**STANDARD_PROFILE, "monthly_bill": 0.0},    "bill = zero"),
        ({**STANDARD_PROFILE, "monthly_bill": -100.0}, "negative bill"),
        ({**STANDARD_PROFILE, "monthly_bill": 100_000.01}, "bill above maximum"),
        # roof_area_sqft out of range
        ({**STANDARD_PROFILE, "roof_area_sqft": 49.99}, "roof below minimum"),
        ({**STANDARD_PROFILE, "roof_area_sqft": 0.0},   "roof = zero"),
        ({**STANDARD_PROFILE, "roof_area_sqft": 5_000.01}, "roof above maximum"),
        # budget out of range
        ({**STANDARD_PROFILE, "budget": 49_999.99},    "budget below minimum"),
        ({**STANDARD_PROFILE, "budget": 0.0},          "budget = zero"),
        ({**STANDARD_PROFILE, "budget": 50_00_000.01}, "budget above maximum"),
    ])
    def test_invalid_input_returns_422(self, client, payload, label):
        status, _ = _post(client, payload)
        assert status == 422, f"{label}: expected 422, got {status}"


class TestAdvisorAllCities:
    """All 15 supported cities return valid AdvisorResponse."""

    @pytest.mark.parametrize("city", ALL_CITIES)
    def test_all_cities_return_200(self, client, city):
        status, data = _post(client, {**STANDARD_PROFILE, "city": city})
        assert status == 200, f"{city}: expected 200, got {status} — {data}"

    @pytest.mark.parametrize("city", ALL_CITIES)
    def test_all_cities_return_valid_recommendation(self, client, city):
        _, data = _post(client, {**STANDARD_PROFILE, "city": city})
        assert data["investment_recommendation"] in VALID_RECOMMENDATIONS

    @pytest.mark.parametrize("city", ALL_CITIES)
    def test_all_cities_return_all_required_fields(self, client, city):
        _, data = _post(client, {**STANDARD_PROFILE, "city": city})
        missing = REQUIRED_FIELDS - set(data.keys())
        assert not missing, f"{city}: missing fields {missing}"

    @pytest.mark.parametrize("city", ALL_CITIES)
    def test_all_cities_positive_system_size(self, client, city):
        _, data = _post(client, {**STANDARD_PROFILE, "city": city})
        assert data["system_size_kw"] >= 1.0

    @pytest.mark.parametrize("city", ALL_CITIES)
    def test_all_cities_city_field_echoed_correctly(self, client, city):
        _, data = _post(client, {**STANDARD_PROFILE, "city": city})
        assert data["city"] == city

    @pytest.mark.parametrize("city", ALL_CITIES)
    def test_all_cities_no_emoji_in_suitability(self, client, city):
        _, data = _post(client, {**STANDARD_PROFILE, "city": city})
        suit = data["suitability"]
        assert "✅" not in suit and "👍" not in suit and "⚠️" not in suit
