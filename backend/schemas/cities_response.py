"""
backend/schemas/cities_response.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PURPOSE
───────
Response contract for GET /cities.

Returns the list of supported city names and slugs.
Used to populate the frontend city selector (Assessment wizard dropdown).

Intentionally minimal per the approved schema plan. Does not return joined
SDSF or Advisor data — that is the responsibility of GET /readiness/{city}
and POST /advisor respectively.

ENDPOINT
────────
  GET /cities

  Consumed by:
    - Assessment wizard city selector dropdown
    - Any frontend component that needs the canonical city list

FIELD SOURCES
─────────────
  CityItem.city      ← sdsf_city_dashboard.csv → City
  CityItem.city_slug ← derived: data_loader._make_slug(city)

LOCATION
────────
  backend/schemas/cities_response.py

DEPENDENCIES
────────────
  pydantic >= 2.0
  No internal imports.

TESTING INSTRUCTIONS
────────────────────
  Run from the backend/ directory:

      python -m schemas.cities_response

  Expected output: all construction and rejection cases pass.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CityItem(BaseModel):
    """
    A single supported city entry.

    One instance per city in sdsf_city_dashboard.csv (15 total).
    """

    model_config = ConfigDict(extra="forbid")

    city: str = Field(
        ...,
        description=(
            "Canonical city name, exactly as it appears in "
            "sdsf_city_dashboard.csv. Case-sensitive."
        ),
        examples=["Bengaluru"],
    )

    city_slug: str = Field(
        ...,
        description=(
            "URL-safe slug derived from the city name. "
            "Used by the frontend to construct API paths and routes "
            "such as /results/{city_slug} and GET /readiness/{city_slug}."
        ),
        examples=["bengaluru"],
    )


class CitiesResponse(BaseModel):
    """
    Response envelope for GET /cities.

    Contains the complete list of supported cities.
    """

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "cities": [
                        {"city": "Ahmedabad", "city_slug": "ahmedabad"},
                        {"city": "Bengaluru", "city_slug": "bengaluru"},
                        {"city": "Bhopal", "city_slug": "bhopal"},
                    ]
                }
            ]
        },
    )

    cities: list[CityItem] = Field(
        ...,
        description="Alphabetically sorted list of all 15 supported cities.",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Smoke test (python -m schemas.cities_response)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json
    import sys
    from pydantic import ValidationError

    _PASS = "✅"
    _FAIL = "❌"
    _errors: list[str] = []

    # All 15 cities as they will be returned by CityService
    _all_cities = [
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

    def check(label: str, should_pass: bool, **kwargs) -> None:
        try:
            CitiesResponse(**kwargs)
            if should_pass:
                print(f"  {_PASS} {label}")
            else:
                msg = f"{label}: expected ValidationError, got valid model"
                print(f"  {_FAIL} {msg}")
                _errors.append(msg)
        except (ValidationError, Exception) as exc:
            if not should_pass:
                print(f"  {_PASS} {label}")
            else:
                msg = f"{label}: unexpected error — {exc}"
                print(f"  {_FAIL} {msg}")
                _errors.append(msg)

    print("\n=== CitiesResponse smoke test ===\n")

    print("Valid construction:")
    check("All 15 cities", should_pass=True, cities=_all_cities)
    check("Single city", should_pass=True,
          cities=[{"city": "Bengaluru", "city_slug": "bengaluru"}])
    check("Empty list accepted", should_pass=True, cities=[])

    print("\nCityItem extra='forbid':")
    try:
        CityItem(city="Bengaluru", city_slug="bengaluru", payback_years=3.7)
        print(f"  {_FAIL} Extra field should have been rejected")
        _errors.append("CityItem extra field not rejected")
    except ValidationError:
        print(f"  {_PASS} Extra field on CityItem rejected")

    print("\nCityItem missing fields:")
    try:
        CityItem(city="Bengaluru")
        print(f"  {_FAIL} Missing city_slug should have been rejected")
        _errors.append("CityItem missing city_slug not rejected")
    except ValidationError:
        print(f"  {_PASS} Missing city_slug rejected")

    try:
        CityItem(city_slug="bengaluru")
        print(f"  {_FAIL} Missing city should have been rejected")
        _errors.append("CityItem missing city not rejected")
    except ValidationError:
        print(f"  {_PASS} Missing city rejected")

    print("\nCitiesResponse missing field:")
    try:
        CitiesResponse()
        print(f"  {_FAIL} Missing cities list should have been rejected")
        _errors.append("CitiesResponse missing cities not rejected")
    except ValidationError:
        print(f"  {_PASS} Missing cities list rejected")

    print("\nJSON round-trip (15 cities):")
    try:
        resp = CitiesResponse(cities=_all_cities)
        serialised = resp.model_dump_json()
        parsed = json.loads(serialised)
        assert len(parsed["cities"]) == 15
        assert parsed["cities"][0]["city"] == "Ahmedabad"
        assert parsed["cities"][1]["city_slug"] == "bengaluru"
        # Confirm no extra fields leaked in
        for item in parsed["cities"]:
            assert set(item.keys()) == {"city", "city_slug"}, \
                f"Unexpected keys in city item: {item.keys()}"
        print(f"  {_PASS} 15 cities serialise correctly")
        print(f"  {_PASS} Each item contains exactly city + city_slug")
    except Exception as exc:
        msg = f"JSON round-trip failed: {exc}"
        print(f"  {_FAIL} {msg}")
        _errors.append(msg)

    print()
    if _errors:
        print(f"❌ {len(_errors)} test(s) failed:")
        for e in _errors:
            print(f"   • {e}")
        sys.exit(1)
    else:
        print("✅ All tests passed.")
