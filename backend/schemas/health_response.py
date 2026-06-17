"""
backend/schemas/health_response.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PURPOSE
───────
Response contract for GET /health.

Minimal liveness check. Confirms the API is running and accepting requests.
No data-layer dependency — the route handler constructs this directly.

ENDPOINT
────────
  GET /health

FIELD SOURCES
─────────────
  status ← hardcoded by route handler: "healthy"

LOCATION
────────
  backend/schemas/health_response.py

DEPENDENCIES
────────────
  pydantic >= 2.0
  No internal imports.

TESTING INSTRUCTIONS
────────────────────
  Run from the backend/ directory:

      python -m schemas.health_response
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """Response for GET /health."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"examples": [{"status": "healthy"}]},
    )

    status: Literal["healthy"] = Field(
        ...,
        description="API liveness status. Always 'healthy' when the service is running.",
        examples=["healthy"],
    )


# ─────────────────────────────────────────────────────────────────────────────
# Smoke test (python -m schemas.health_response)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json
    import sys
    from pydantic import ValidationError

    _PASS = "✅"
    _FAIL = "❌"
    _errors: list[str] = []

    def check(label: str, should_pass: bool, **kwargs) -> None:
        try:
            HealthResponse(**kwargs)
            if should_pass:
                print(f"  {_PASS} {label}")
            else:
                msg = f"{label}: expected ValidationError"
                print(f"  {_FAIL} {msg}")
                _errors.append(msg)
        except ValidationError:
            if not should_pass:
                print(f"  {_PASS} {label}")
            else:
                msg = f"{label}: unexpected ValidationError"
                print(f"  {_FAIL} {msg}")
                _errors.append(msg)

    print("\n=== HealthResponse smoke test ===\n")

    print("Valid:")
    check("status='healthy'", should_pass=True, status="healthy")

    print("\nInvalid:")
    check("status='ok' rejected",      should_pass=False, status="ok")
    check("status='running' rejected", should_pass=False, status="running")
    check("Missing status rejected",   should_pass=False)
    check("Extra field rejected",      should_pass=False,
          status="healthy", version="1.0")

    print("\nJSON round-trip:")
    try:
        resp = HealthResponse(status="healthy")
        parsed = json.loads(resp.model_dump_json())
        assert parsed == {"status": "healthy"}
        print(f"  {_PASS} Serialises to {{\"status\": \"healthy\"}}")
    except Exception as exc:
        msg = f"Round-trip failed: {exc}"
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
