"""
backend/services/methodology_service.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PURPOSE
───────
Service layer for GET /methodology.

Returns a static MethodologyResponse containing the project title,
description, and version string for the How It Works and About pages.

Contains no calculations, no CSV access, and no DataLoader dependency.

RESPONSIBILITIES
────────────────
  Single public method:

    get_methodology() → MethodologyResponse

  Returns a pre-constructed, immutable MethodologyResponse.
  Built once at class instantiation — all calls return the same object.

LOCATION
────────
  backend/services/methodology_service.py

DEPENDENCIES
────────────
  schemas.methodology_response — MethodologyResponse only.
  No DataLoader. No calculations. No utils.

TESTING INSTRUCTIONS
────────────────────
  Run from the backend/ directory:

      python -m services.methodology_service

  Expected output: all cases pass.
"""

from __future__ import annotations

import logging

from schemas.methodology_response import MethodologyResponse

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Static methodology metadata
# These strings are frozen project-level constants — they describe the
# dissertation research and do not change per request or per city.
# ─────────────────────────────────────────────────────────────────────────────

_TITLE: str = "AI-Powered Residential Solar Investment Advisor"

_DESCRIPTION: str = (
    "Explainable solar investment recommendations for 15 Indian cities, "
    "derived from an XGBoost model trained on 5 years of NASA POWER "
    "meteorological data with SHAP-based explainability."
)

_VERSION: str = "1.0"


class MethodologyService:
    """
    Service for GET /methodology.

    Stateless and dependency-free.
    The MethodologyResponse is constructed once at instantiation and
    returned on every call — no per-request work is performed.
    """

    def __init__(self) -> None:
        # Build once; reuse on every call.
        self._response = MethodologyResponse(
            title=_TITLE,
            description=_DESCRIPTION,
            version=_VERSION,
        )

    def get_methodology(self) -> MethodologyResponse:
        """
        Return the project methodology metadata.

        Returns
        -------
        MethodologyResponse
            Static project title, description, and version string.
            Never raises — no I/O, no DataLoader dependency.
        """
        logger.debug("[methodology_service] Serving methodology metadata.")
        return self._response


# ─────────────────────────────────────────────────────────────────────────────
# Module-level singleton
# Imported by the route handler:
#
#     from services.methodology_service import methodology_service
# ─────────────────────────────────────────────────────────────────────────────

methodology_service = MethodologyService()


# ─────────────────────────────────────────────────────────────────────────────
# Smoke test (python -m services.methodology_service)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json
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

    svc = MethodologyService()

    print("\n=== MethodologyService smoke test ===\n")

    print("Return type and fields:")
    resp = svc.get_methodology()

    if isinstance(resp, MethodologyResponse):
        ok("Returns MethodologyResponse")
    else:
        fail(f"Expected MethodologyResponse, got {type(resp)}")

    if resp.title == _TITLE:
        ok(f"title = {resp.title!r}")
    else:
        fail(f"title mismatch: {resp.title!r}")

    if resp.description == _DESCRIPTION:
        ok("description matches expected string")
    else:
        fail(f"description mismatch: {resp.description!r}")

    if resp.version == _VERSION:
        ok(f"version = {resp.version!r}")
    else:
        fail(f"version mismatch: {resp.version!r}")

    print("\nIdempotency (same object returned every call):")
    resp2 = svc.get_methodology()
    resp3 = svc.get_methodology()
    if resp is resp2 is resp3:
        ok("get_methodology() returns the same object on every call")
    else:
        fail("get_methodology() returned different objects across calls")

    print("\nJSON serialisation:")
    try:
        parsed = json.loads(resp.model_dump_json())
        assert set(parsed.keys()) == {"title", "description", "version"}
        assert parsed["version"] == "1.0"
        assert "XGBoost" in parsed["description"]
        ok("Serialises to exactly {title, description, version}")
        ok("No extra metrics in serialised output")
    except Exception as exc:
        fail(f"Serialisation failed: {exc}")

    print("\nSingleton:")
    if isinstance(methodology_service, MethodologyService):
        ok("Module-level methodology_service is a MethodologyService instance")
    else:
        fail(f"Expected MethodologyService, got {type(methodology_service)}")

    singleton_resp = methodology_service.get_methodology()
    if singleton_resp.title == _TITLE:
        ok("Singleton get_methodology() returns correct title")
    else:
        fail(f"Singleton returned wrong title: {singleton_resp.title!r}")

    print()
    if _errors:
        print(f"❌ {len(_errors)} test(s) failed:")
        for e in _errors:
            print(f"   • {e}")
        sys.exit(1)
    else:
        print("✅ All tests passed.")
