"""
backend/tests/test_cities.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tests for GET /cities.

Verifies:
  - HTTP 200 response
  - Returns exactly 15 supported cities
  - Every city item contains exactly {city, city_slug}
  - City names match the CSV exactly (case-sensitive)
  - Slugs are lowercase, hyphen-separated, derived correctly
  - No duplicate city names or slugs
  - Cities are sorted alphabetically
  - Response structure matches CitiesResponse schema
"""

from __future__ import annotations

import pytest


# The exact 15 supported cities sourced from sdsf_city_dashboard.csv.
# This list is the ground truth for all city-related assertions.
EXPECTED_CITIES: list[dict[str, str]] = [
    {"city": "Ahmedabad",   "city_slug": "ahmedabad"},
    {"city": "Bengaluru",   "city_slug": "bengaluru"},
    {"city": "Bhopal",      "city_slug": "bhopal"},
    {"city": "Bhubaneswar", "city_slug": "bhubaneswar"},
    {"city": "Chandigarh",  "city_slug": "chandigarh"},
    {"city": "Chennai",     "city_slug": "chennai"},
    {"city": "Delhi",       "city_slug": "delhi"},
    {"city": "Guwahati",    "city_slug": "guwahati"},
    {"city": "Hyderabad",   "city_slug": "hyderabad"},
    {"city": "Jaipur",      "city_slug": "jaipur"},
    {"city": "Kochi",       "city_slug": "kochi"},
    {"city": "Kolkata",     "city_slug": "kolkata"},
    {"city": "Mangalore",   "city_slug": "mangalore"},
    {"city": "Mumbai",      "city_slug": "mumbai"},
    {"city": "Pune",        "city_slug": "pune"},
]

EXPECTED_CITY_NAMES: list[str] = [c["city"] for c in EXPECTED_CITIES]
EXPECTED_SLUGS: list[str]      = [c["city_slug"] for c in EXPECTED_CITIES]


class TestCities:
    """Tests for GET /cities."""

    @pytest.fixture(autouse=True)
    def response(self, client):
        """Fetch /cities once per test via the shared session client."""
        self._response = client.get("/cities")
        self._data = self._response.json()

    def test_returns_200(self):
        assert self._response.status_code == 200

    def test_content_type_is_json(self):
        assert "application/json" in self._response.headers["content-type"]

    def test_response_has_cities_key(self):
        assert "cities" in self._data

    def test_returns_exactly_15_cities(self):
        assert len(self._data["cities"]) == 15

    def test_each_city_item_has_exactly_two_fields(self):
        for item in self._data["cities"]:
            assert set(item.keys()) == {"city", "city_slug"}, (
                f"Unexpected fields in city item: {set(item.keys())}"
            )

    def test_city_names_match_csv_exactly(self):
        returned_names = [item["city"] for item in self._data["cities"]]
        assert returned_names == EXPECTED_CITY_NAMES

    def test_city_slugs_match_expected_derivation(self):
        returned_slugs = [item["city_slug"] for item in self._data["cities"]]
        assert returned_slugs == EXPECTED_SLUGS

    def test_no_duplicate_city_names(self):
        names = [item["city"] for item in self._data["cities"]]
        assert len(names) == len(set(names))

    def test_no_duplicate_slugs(self):
        slugs = [item["city_slug"] for item in self._data["cities"]]
        assert len(slugs) == len(set(slugs))

    def test_cities_are_sorted_alphabetically(self):
        names = [item["city"] for item in self._data["cities"]]
        assert names == sorted(names)

    def test_slugs_are_lowercase(self):
        for item in self._data["cities"]:
            assert item["city_slug"] == item["city_slug"].lower(), (
                f"Slug not lowercase: {item['city_slug']}"
            )

    def test_slugs_contain_no_spaces(self):
        for item in self._data["cities"]:
            assert " " not in item["city_slug"]

    def test_slugs_contain_no_emoji(self):
        for item in self._data["cities"]:
            assert item["city_slug"].isascii(), (
                f"Non-ASCII characters in slug: {item['city_slug']}"
            )

    def test_all_expected_cities_present(self):
        returned = {item["city"] for item in self._data["cities"]}
        missing = set(EXPECTED_CITY_NAMES) - returned
        assert not missing, f"Missing cities: {missing}"

    def test_no_unexpected_cities_present(self):
        returned = {item["city"] for item in self._data["cities"]}
        unexpected = returned - set(EXPECTED_CITY_NAMES)
        assert not unexpected, f"Unexpected cities: {unexpected}"
