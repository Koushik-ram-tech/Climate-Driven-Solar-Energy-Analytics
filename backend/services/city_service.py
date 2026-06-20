"""
backend/services/city_service.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PURPOSE
───────
Service layer for GET /cities.

Translates the DataLoader city index into a CitiesResponse schema object.
Contains no business logic, no calculations, and no notebook code.

RESPONSIBILITIES
────────────────
  Single public method:

    get_all_cities() → CitiesResponse

  Reads city names and slugs from the DataLoader singleton.
  Constructs and returns a CitiesResponse containing one CityItem per
  supported city, sorted alphabetically (order inherited from DataLoader).

WHAT THIS SERVICE DOES NOT DO
──────────────────────────────
  ✗ Read CSV files directly
  ✗ Use pandas
  ✗ Compute slugs (pre-computed by DataLoader._make_slug at startup)
  ✗ Filter, rank, or sort cities by any metric
  ✗ Perform SDSF or investment calculations
  ✗ Implement recommendation logic
  ✗ Define FastAPI routes
  ✗ Serialise responses (route handler's responsibility)

LOCATION
────────
  backend/services/city_service.py

DEPENDENCIES
────────────
  data.data_loader   — loader singleton, DataLoaderError
  schemas.cities_response — CityItem, CitiesResponse

ERROR HANDLING
──────────────
  DataLoaderError: raised by loader._assert_loaded() if load() was never
    called. Not caught here — propagates to the route handler which maps
    it to HTTP 500. This is a startup configuration failure, not a
    per-request error.

  KeyError from get_sdsf_row(): structurally impossible in get_all_cities()
    because every name returned by city_list() is guaranteed to exist in
    sdsf_index. No try/except required.

TESTING INSTRUCTIONS
────────────────────
  Run from the backend/ directory:

      python -m services.city_service

  Expected output: all cases pass.

  Key cases for Phase 5 integration tests:
    - Returns exactly 15 CityItem objects
    - City names match sdsf_city_dashboard.csv exactly
    - Slugs match DataLoader derivation (lowercase, hyphens)
    - Return type is CitiesResponse
    - Cities are sorted alphabetically
"""

from __future__ import annotations

import logging

from data.data_loader import loader
from schemas.cities_response import CityItem, CitiesResponse

logger = logging.getLogger(__name__)


class CityService:
    """
    Service for GET /cities.

    Stateless — holds no data of its own.
    All data is read from the DataLoader singleton on each call.
    Safe to instantiate once at application startup and reuse.
    """

    def get_all_cities(self) -> CitiesResponse:
        """
        Return the complete list of supported cities.

        Reads city names from DataLoader.city_list() (sorted alphabetically)
        and retrieves the corresponding city_slug from each SDSFRow.

        Returns
        -------
        CitiesResponse
            Contains one CityItem per supported city.

        Raises
        ------
        DataLoaderError
            If DataLoader.load() has not been called before this method.
            Propagates to the route handler — not caught here.
        """
        city_names = loader.city_list()

        items = []

        for name in city_names:
            row = loader.get_sdsf_row(name)

            items.append(
                CityItem(
                    city=row.city,
                    city_slug=row.city_slug,
                )
    )

        logger.debug("[city_service] Returning %d cities.", len(items))
        return CitiesResponse(cities=items)


# ─────────────────────────────────────────────────────────────────────────────
# Module-level singleton
# Instantiated once; imported by the route handler:
#
#     from services.city_service import city_service
# ─────────────────────────────────────────────────────────────────────────────

city_service = CityService()


# ─────────────────────────────────────────────────────────────────────────────
# Smoke test (python -m services.city_service)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import os
    import sys

    logging.basicConfig(level=logging.WARNING, format="%(message)s")

    _PASS = "✅"
    _FAIL = "❌"
    _errors: list[str] = []

    def fail(msg: str) -> None:
        print(f"  {_FAIL} {msg}")
        _errors.append(msg)

    def ok(msg: str) -> None:
        print(f"  {_PASS} {msg}")

    # ── Bootstrap DataLoader with real CSVs ───────────────────────────────────
    _here = os.path.dirname(os.path.abspath(__file__))
    _data_dir = os.path.join(_here, "..", "data")
    _sdsf_path    = os.path.join(_data_dir, "sdsf_city_dashboard.csv")
    _advisor_path = os.path.join(_data_dir, "solar_investment_advisor_results.csv")

    print("\n=== CityService smoke test ===\n")
    print("Bootstrapping DataLoader...")
    try:
        loader.load(_sdsf_path, _advisor_path)
        print("  DataLoader ready.\n")
    except DataLoaderError as exc:
        print(f"  {_FAIL} DataLoader failed: {exc}", file=sys.stderr)
        sys.exit(1)

    # ── Test: before-load guard (separate instance) ───────────────────────────
    # Cannot test here without a second unloaded loader instance — covered in
    # Phase 5 unit tests using a mock loader.

    # ── Test: get_all_cities() returns CitiesResponse ─────────────────────────
    print("Return type and count:")
    svc = CityService()
    result = svc.get_all_cities()

    from schemas.cities_response import CitiesResponse as _CR
    if isinstance(result, _CR):
        ok("Return type is CitiesResponse")
    else:
        fail(f"Expected CitiesResponse, got {type(result)}")

    if len(result.cities) == 15:
        ok("Returns exactly 15 CityItem objects")
    else:
        fail(f"Expected 15 cities, got {len(result.cities)}")

    # ── Test: all expected city names present ─────────────────────────────────
    print("\nCity names:")
    _expected_cities = [
        "Ahmedabad", "Bengaluru", "Bhopal", "Bhubaneswar", "Chandigarh",
        "Chennai", "Delhi", "Guwahati", "Hyderabad", "Jaipur",
        "Kochi", "Kolkata", "Mangalore", "Mumbai", "Pune",
    ]
    returned_names = [item.city for item in result.cities]
    if returned_names == _expected_cities:
        ok("All 15 city names match CSV exactly and are sorted alphabetically")
    else:
        missing = set(_expected_cities) - set(returned_names)
        extra   = set(returned_names) - set(_expected_cities)
        fail(f"City name mismatch. Missing: {missing}. Extra: {extra}")

    # ── Test: slugs match expected derivation ─────────────────────────────────
    print("\nCity slugs:")
    _expected_slugs = {
        "Ahmedabad": "ahmedabad", "Bengaluru": "bengaluru",
        "Bhopal": "bhopal", "Bhubaneswar": "bhubaneswar",
        "Chandigarh": "chandigarh", "Chennai": "chennai",
        "Delhi": "delhi", "Guwahati": "guwahati",
        "Hyderabad": "hyderabad", "Jaipur": "jaipur",
        "Kochi": "kochi", "Kolkata": "kolkata",
        "Mangalore": "mangalore", "Mumbai": "mumbai", "Pune": "pune",
    }
    slug_errors = [
        f"{item.city}: expected '{_expected_slugs[item.city]}', got '{item.city_slug}'"
        for item in result.cities
        if item.city_slug != _expected_slugs.get(item.city)
    ]
    if not slug_errors:
        ok("All 15 slugs match expected derivation")
    else:
        for e in slug_errors:
            fail(e)

    # ── Test: CityItem contains exactly two fields ────────────────────────────
    print("\nSchema contract:")
    sample = result.cities[0]
    item_keys = set(sample.model_dump().keys())
    if item_keys == {"city", "city_slug"}:
        ok("CityItem contains exactly {city, city_slug} — no extra fields")
    else:
        fail(f"Unexpected CityItem fields: {item_keys}")

    # ── Test: alphabetical order preserved ───────────────────────────────────
    names = [item.city for item in result.cities]
    if names == sorted(names):
        ok("Cities are sorted alphabetically")
    else:
        fail(f"Cities are not sorted. Got: {names}")

    # ── Test: module-level singleton is same type ─────────────────────────────
    print("\nSingleton:")
    if isinstance(city_service, CityService):
        ok("Module-level city_service is a CityService instance")
    else:
        fail(f"Expected CityService, got {type(city_service)}")

    singleton_result = city_service.get_all_cities()
    if len(singleton_result.cities) == 15:
        ok("Singleton get_all_cities() returns correct count")
    else:
        fail("Singleton returned wrong count")

    # ── Result ────────────────────────────────────────────────────────────────
    print()
    if _errors:
        print(f"❌ {len(_errors)} test(s) failed:")
        for e in _errors:
            print(f"   • {e}")
        sys.exit(1)
    else:
        print("✅ All tests passed.")
