"""
backend/services/readiness_service.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PURPOSE
───────
Service layer for GET /readiness/{city}.

Translates one SDSFRow from the DataLoader into one ReadinessResponse.
Pure field mapping — no computation, no business logic, no notebook code.

RESPONSIBILITIES
────────────────
  Single public method:

    get_readiness(city: str) → ReadinessResponse

  Accepts a city name or URL slug.
  Resolves it to the canonical city name via DataLoader.
  Fetches the SDSFRow.
  Maps every field 1-to-1 into ReadinessResponse.
  Returns the schema object to the route handler.

WHAT THIS SERVICE DOES NOT DO
──────────────────────────────
  ✗ Read CSV files directly
  ✗ Use pandas
  ✗ Perform SDSF calculations
  ✗ Perform financial or investment calculations
  ✗ Access the Advisor CSV (get_advisor_row is never called)
  ✗ Implement recommendation logic
  ✗ Strip emoji from Suitability (DataLoader already did this)
  ✗ Define FastAPI routes
  ✗ Serialise responses (route handler's responsibility)

LOCATION
────────
  backend/services/readiness_service.py

DEPENDENCIES
────────────
  data.data_loader      — loader singleton
  utils.exceptions      — CityNotFoundError, DataLoaderError
  schemas.readiness_response — ReadinessResponse

ERROR HANDLING
──────────────
  CityNotFoundError:
    Raised when loader.resolve_city() cannot match the input to any
    supported city name or slug. Caught by the Phase 4 route handler
    and mapped to HTTP 404.

  DataLoaderError:
    Raised by loader._assert_loaded() if DataLoader.load() was never
    called. Not caught here — propagates to the route handler and maps
    to HTTP 500. This is a startup configuration failure, not a per-
    request error.

TESTING INSTRUCTIONS
────────────────────
  Run from the backend/ directory:

      python -m services.readiness_service

  Expected output: all cases pass.

  Key cases for Phase 5 integration tests:
    - Valid city name returns correct ReadinessResponse
    - Valid city slug returns correct ReadinessResponse
    - Unsupported city raises CityNotFoundError
    - Empty string raises CityNotFoundError
    - Return value is always ReadinessResponse (never a dict or SDSFRow)
    - suitability field contains clean label (no emoji)
    - All 15 cities return without error
"""

from __future__ import annotations

import logging

from data.data_loader import loader
from schemas.readiness_response import ReadinessResponse
from utils.exceptions import CityNotFoundError  # noqa: F401 — DataLoaderError re-exported for route handler imports

logger = logging.getLogger(__name__)


class ReadinessService:
    """
    Service for GET /readiness/{city}.

    Stateless — holds no data of its own.
    All data is read from the DataLoader singleton on each call.
    Safe to instantiate once at application startup and reuse.
    """

    def get_readiness(self, city: str) -> ReadinessResponse:
        """
        Return SDSF outputs for a single city.

        Parameters
        ----------
        city : str
            City name (e.g. "Bengaluru") or URL slug (e.g. "bengaluru").
            Case-sensitive for names; slugs are lowercase.

        Returns
        -------
        ReadinessResponse
            Complete SDSF output for the requested city.

        Raises
        ------
        CityNotFoundError
            If the value does not resolve to any supported city.
            Route handler maps this to HTTP 404.
        DataLoaderError
            If DataLoader.load() was not called at startup.
            Route handler maps this to HTTP 500.
        """
        try:
            canonical = loader.resolve_city(city)
        except KeyError as exc:
            raise CityNotFoundError(
                f"City not supported: {city!r}. "
                f"Supported cities: {loader.city_list()}"
            ) from exc

        row = loader.get_sdsf_row(canonical)

        logger.debug("[readiness_service] Serving readiness for '%s'.", canonical)

        return ReadinessResponse(
            city=row.city,
            city_slug=row.city_slug,
            mean_ghi=row.mean_ghi,
            p10_ghi=row.p10_ghi,
            p50_ghi=row.p50_ghi,
            p90_ghi=row.p90_ghi,
            reliability_score=row.reliability_score,
            rs_category=row.rs_category,
            model_rmse=row.model_rmse,
            model_mape=row.model_mape,
            prediction_confidence=row.prediction_confidence,
            suitability=row.suitability,       # already clean (no emoji) — DataLoader strips at load time
            explanation=row.explanation,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Module-level singleton
# Imported by the route handler:
#
#     from services.readiness_service import readiness_service
# ─────────────────────────────────────────────────────────────────────────────

readiness_service = ReadinessService()


# ─────────────────────────────────────────────────────────────────────────────
# Smoke test (python -m services.readiness_service)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import os
    import sys

    logging.basicConfig(level=logging.WARNING, format="%(message)s")

    _PASS = "✅"
    _FAIL = "❌"
    _errors: list[str] = []

    def ok(msg: str) -> None:
        print(f"  {_PASS} {msg}")

    def fail(msg: str) -> None:
        print(f"  {_FAIL} {msg}")
        _errors.append(msg)

    # ── Bootstrap DataLoader ──────────────────────────────────────────────────
    _here = os.path.dirname(os.path.abspath(__file__))
    _data_dir = os.path.join(_here, "..", "data")
    _sdsf_path    = os.path.join(_data_dir, "sdsf_city_dashboard.csv")
    _advisor_path = os.path.join(_data_dir, "solar_investment_advisor_results.csv")

    print("\n=== ReadinessService smoke test ===\n")
    print("Bootstrapping DataLoader...")
    try:
        loader.load(_sdsf_path, _advisor_path)
        print("  DataLoader ready.\n")
    except Exception as exc:
        print(f"  {_FAIL} DataLoader failed: {exc}", file=sys.stderr)
        sys.exit(1)

    svc = ReadinessService()

    # ── Valid city name ───────────────────────────────────────────────────────
    print("Valid city name:")
    try:
        resp = svc.get_readiness("Bengaluru")
        if isinstance(resp, ReadinessResponse):
            ok("Returns ReadinessResponse")
        else:
            fail(f"Expected ReadinessResponse, got {type(resp)}")

        # Spot-check field values against known CSV values
        checks = [
            ("city",                  resp.city,                  "Bengaluru"),
            ("city_slug",             resp.city_slug,             "bengaluru"),
            ("mean_ghi",              resp.mean_ghi,              5.272),
            ("p10_ghi",               resp.p10_ghi,               3.58),
            ("p50_ghi",               resp.p50_ghi,               5.37),
            ("p90_ghi",               resp.p90_ghi,               6.88),
            ("reliability_score",     resp.reliability_score,     81.1),
            ("rs_category",           resp.rs_category,           "Consistent Producer"),
            ("prediction_confidence", resp.prediction_confidence, "High"),
            ("suitability",           resp.suitability,           "Highly Suitable"),
        ]
        all_match = True
        for field, actual, expected in checks:
            if actual != expected:
                fail(f"  {field}: expected {expected!r}, got {actual!r}")
                all_match = False
        if all_match:
            ok("All spot-checked field values match CSV")

        # Confirm no emoji in suitability
        if "✅" not in resp.suitability and "👍" not in resp.suitability:
            ok("suitability contains no emoji (clean label)")
        else:
            fail(f"Emoji found in suitability: {resp.suitability!r}")

        # Confirm explanation is non-empty string
        if isinstance(resp.explanation, str) and len(resp.explanation) > 10:
            ok("explanation is a non-empty string")
        else:
            fail(f"Unexpected explanation: {resp.explanation!r}")

    except Exception as exc:
        fail(f"get_readiness('Bengaluru') raised unexpected {type(exc).__name__}: {exc}")

    # ── Valid city slug ───────────────────────────────────────────────────────
    print("\nValid city slug:")
    try:
        resp_slug = svc.get_readiness("bengaluru")
        if resp_slug.city == "Bengaluru" and resp_slug.city_slug == "bengaluru":
            ok("Slug 'bengaluru' resolves to Bengaluru correctly")
        else:
            fail(f"Slug resolution wrong: city={resp_slug.city!r}, slug={resp_slug.city_slug!r}")
    except Exception as exc:
        fail(f"get_readiness('bengaluru') raised {type(exc).__name__}: {exc}")

        # ── All 15 cities succeed ─────────────────────────────────────────────────
        city_errors = []

    for city_name in loader.city_list():
        try:
            r = svc.get_readiness(city_name)
            assert r.city == city_name, f"city mismatch: {r.city!r}"
            assert isinstance(r.mean_ghi, float) and r.mean_ghi > 0
            assert isinstance(r.reliability_score, float)
            assert "✅" not in r.suitability
        except Exception as exc:
            city_errors.append(f"{city_name}: {exc}")
    if city_errors:
        for e in city_errors:
            fail(e)
    else:
        ok("All 15 cities return valid ReadinessResponse with no emoji in suitability")

    # ── All 15 slugs succeed ──────────────────────────────────────────────────
    print("\nAll 15 slugs:")
    slug_errors = []

    for slug in loader.slug_to_city.keys():
        try:
            r = svc.get_readiness(slug)
            assert r.city_slug == slug, f"slug mismatch: {r.city_slug!r}"
        except Exception as exc:
            slug_errors.append(f"{slug}: {exc}")
    if slug_errors:
        for e in slug_errors:
            fail(e)
    else:
        ok("All 15 slugs resolve correctly")

    # ── Invalid city raises CityNotFoundError ─────────────────────────────────
    print("\nInvalid city handling:")
    invalid_cases = [
        ("Varanasi",    "unsupported city name"),
        ("bengalooru",  "misspelled slug"),
        ("",            "empty string"),
        ("BENGALURU",   "wrong case"),
    ]
    for invalid, label in invalid_cases:
        try:
            svc.get_readiness(invalid)
            fail(f"{label} ({invalid!r}) should have raised CityNotFoundError")
        except CityNotFoundError:
            ok(f"{label} ({invalid!r}) raises CityNotFoundError")
        except Exception as exc:
            fail(f"{label} ({invalid!r}) raised wrong exception {type(exc).__name__}: {exc}")

    # ── Return type is never a dict or SDSFRow ────────────────────────────────
    print("\nReturn type contract:")
    resp_type = svc.get_readiness("Delhi")
    if type(resp_type).__name__ == "ReadinessResponse":
        ok("Return type is ReadinessResponse (not dict, not SDSFRow)")
    else:
        fail(f"Wrong return type: {type(resp_type)}")

    # ── Singleton instance ────────────────────────────────────────────────────
    print("\nSingleton:")
    if isinstance(readiness_service, ReadinessService):
        ok("Module-level readiness_service is a ReadinessService instance")
    else:
        fail(f"Expected ReadinessService, got {type(readiness_service)}")

    singleton_resp = readiness_service.get_readiness("Pune")
    if singleton_resp.city == "Pune":
        ok("Singleton get_readiness('Pune') returns correct city")
    else:
        fail(f"Singleton returned wrong city: {singleton_resp.city!r}")

    # ── Result ────────────────────────────────────────────────────────────────
    print()
    if _errors:
        print(f"❌ {len(_errors)} test(s) failed:")
        for e in _errors:
            print(f"   • {e}")
        sys.exit(1)
    else:
        print("✅ All tests passed.")
