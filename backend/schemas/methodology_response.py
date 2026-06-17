"""
backend/schemas/methodology_response.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PURPOSE
───────
Response contract for GET /methodology.

Minimal informational payload for the How It Works and About pages.
Provides the project title, a brief description, and a version string.

Research statistics (R², RMSE, city count, date range) are static copy
concerns handled by the frontend — they are not served through this API.

ENDPOINT
────────
  GET /methodology

  Consumed by:
    - /how-it-works page
    - /about page

FIELD SOURCES
─────────────
  title       ← static: project title
  description ← static: one-sentence product description
  version     ← static: framework version string

LOCATION
────────
  backend/schemas/methodology_response.py

DEPENDENCIES
────────────
  pydantic >= 2.0
  No internal imports.

TESTING INSTRUCTIONS
────────────────────
  Run from the backend/ directory:

      python -m schemas.methodology_response
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class MethodologyResponse(BaseModel):
    """Response for GET /methodology."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "title": "AI-Powered Residential Solar Investment Advisor",
                    "description": (
                        "Explainable solar investment recommendations for 15 Indian "
                        "cities, derived from an XGBoost model trained on 5 years of "
                        "NASA POWER meteorological data with SHAP-based explainability."
                    ),
                    "version": "1.0",
                }
            ]
        },
    )

    title: str = Field(
        ...,
        description="Project title.",
        examples=["AI-Powered Residential Solar Investment Advisor"],
    )

    description: str = Field(
        ...,
        description="One-sentence description of the product and its methodology.",
        examples=[
            "Explainable solar investment recommendations for 15 Indian cities, "
            "derived from an XGBoost model trained on 5 years of NASA POWER "
            "meteorological data with SHAP-based explainability."
        ],
    )

    version: str = Field(
        ...,
        description="Framework version string.",
        examples=["1.0"],
    )


# ─────────────────────────────────────────────────────────────────────────────
# Smoke test (python -m schemas.methodology_response)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json
    import sys
    from pydantic import ValidationError

    _PASS = "✅"
    _FAIL = "❌"
    _errors: list[str] = []

    _valid = {
        "title": "AI-Powered Residential Solar Investment Advisor",
        "description": (
            "Explainable solar investment recommendations for 15 Indian cities."
        ),
        "version": "1.0",
    }

    def check(label: str, should_pass: bool, **kwargs) -> None:
        try:
            MethodologyResponse(**kwargs)
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

    print("\n=== MethodologyResponse smoke test ===\n")

    print("Valid:")
    check("Standard construction", should_pass=True, **_valid)

    print("\nMissing fields:")
    for field in ["title", "description", "version"]:
        data = {k: v for k, v in _valid.items() if k != field}
        check(f"Missing '{field}' rejected", should_pass=False, **data)

    print("\nextra='forbid':")
    check("model_r2 as extra field rejected", should_pass=False,
          **_valid, model_r2=0.8831)
    check("cities_count as extra field rejected", should_pass=False,
          **_valid, cities_count=15)

    print("\nJSON round-trip:")
    try:
        resp = MethodologyResponse(**_valid)
        parsed = json.loads(resp.model_dump_json())
        assert set(parsed.keys()) == {"title", "description", "version"}
        assert parsed["version"] == "1.0"
        print(f"  {_PASS} Serialises with exactly 3 fields")
        print(f"  {_PASS} No extra metrics in output")
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
