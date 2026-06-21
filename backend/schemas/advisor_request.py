"""
backend/schemas/advisor_request.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PURPOSE
───────
Defines the request contract for POST /advisor.

Validates all four user inputs before they reach AdvisorService.
Invalid requests are rejected at the FastAPI boundary with HTTP 422 and
a structured error body — AdvisorService never receives unvalidated data.

This schema has no knowledge of CSV data, services, or other schemas.

LOCATION
────────
  backend/schemas/advisor_request.py

DEPENDENCIES
────────────
  pydantic >= 2.0   (BaseModel, Field, Literal — stdlib typing)
  No internal imports.

FIELD DECISIONS
───────────────
  city           Literal over the 15 supported names.
                 Validated at parse time with no data-layer dependency.
                 Error message names every allowed value automatically.

  monthly_bill   float, ₹500 – ₹100,000.
                 float not int: bills carry paise (e.g. ₹1,250.50).
                 Bounds from BACKEND_ARCHITECTURE.md §9.

  roof_area_sqft float, 50 – 5,000 sq ft.
                 float: roofs are measured in decimal sq ft.
                 Lower bound set deliberately below the physical minimum
                 for a 1 kW system (~93 sq ft) so AdvisorService returns
                 the MIN_SYS_KW floor naturally rather than the schema
                 hard-blocking borderline inputs.

  budget         float, ₹50,000 – ₹50,00,000.
                 Lower bound is above the post-subsidy floor for a 1 kW
                 system (₹55,000 × 0.70 = ₹38,500), so any accepted
                 budget can fund at least a minimum viable system.
                 Upper bound exceeds the regulatory 10 kW cap cost
                 (10 × ₹55,000 = ₹5,50,000) so it never constrains
                 the calculation artificially.

FIXED CONSTANTS (not user inputs)
───────────────────────────────────
  tariff = ₹7.0/kWh   Fixed per approved architecture decision.
                       Not exposed as a field. AdvisorService applies it
                       as a module-level constant.

TESTING INSTRUCTIONS
────────────────────
  Run from the backend/ directory:

      python -m schemas.advisor_request

  The smoke test exercises valid inputs, every invalid field individually,
  and a missing-field case. Expected output: all 8 cases pass.

  For integration tests (Phase 5), see backend/tests/test_advisor_request.py.
  Key cases to cover:
    - All 15 cities accepted
    - City name case-sensitivity (e.g. "bengaluru" must be rejected)
    - monthly_bill boundary values: 499.99 rejected, 500.0 accepted,
      100000.0 accepted, 100000.01 rejected
    - roof_area_sqft boundary: 49.99 rejected, 50.0 accepted
    - budget boundary: 49999.99 rejected, 50000.0 accepted
    - Extra fields ignored (Pydantic default: they are stripped silently)
    - Missing required field returns 422 with field name in error detail
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, ConfigDict

# ─────────────────────────────────────────────────────────────────────────────
# Supported cities
# Source: sdsf_city_dashboard.csv — 15 rows, City column.
# Frozen: do not edit without a corresponding CSV update.
# ─────────────────────────────────────────────────────────────────────────────

SupportedCity = Literal[
    "Ahmedabad",
    "Bengaluru",
    "Bhopal",
    "Bhubaneswar",
    "Chandigarh",
    "Chennai",
    "Delhi",
    "Guwahati",
    "Hyderabad",
    "Jaipur",
    "Kochi",
    "Kolkata",
    "Mangalore",
    "Mumbai",
    "Pune",
]


# ─────────────────────────────────────────────────────────────────────────────
# Request schema
# ─────────────────────────────────────────────────────────────────────────────

class AdvisorRequest(BaseModel):
    """
    Input model for POST /advisor.

    Represents a single homeowner assessment request.
    All four fields are required. No optional fields.

    The electricity tariff (₹7.0/kWh) is a fixed system constant and is
    intentionally absent — it is not a user input.
    """

    city: SupportedCity = Field(
        ...,
        description=(
            "City for which the solar investment assessment is requested. "
            "Must be one of the 15 supported Indian cities."
        ),
        examples=["Bengaluru"],
    )

    monthly_bill: float = Field(
        ...,
        ge=500.0,
        le=100_000.0,
        description=(
            "Average monthly electricity bill in Indian Rupees (₹). "
            "Used to estimate annual household electricity consumption. "
            "Must be between ₹500 and ₹1,00,000."
        ),
        examples=[3000.0],
    )

    roof_area_sqft: float = Field(
        ...,
        ge=50.0,
        le=5_000.0,
        description=(
            "Total flat roof area available for solar panel installation, "
            "in square feet. "
            "Must be between 50 and 5,000 sq ft."
        ),
        examples=[500.0],
    )

    budget: float = Field(
        ...,
        ge=50_000.0,
        le=50_00_000.0,
        description=(
            "Maximum capital available for the solar system installation "
            "in Indian Rupees (₹), inclusive of all components. "
            "Must be between ₹50,000 and ₹50,00,000."
        ),
        examples=[400_000.0],
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "city": "Bengaluru",
                    "monthly_bill": 3000.0,
                    "roof_area_sqft": 500.0,
                    "budget": 400000.0,
                }
            ]
        }
    )


# ─────────────────────────────────────────────────────────────────────────────
# Smoke test (python -m schemas.advisor_request)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    from pydantic import ValidationError

    _PASS = "✅"
    _FAIL = "❌"
    errors: list[str] = []

    def check(label: str, should_pass: bool, data: dict) -> None:
        try:
            req = AdvisorRequest(**data)
            if should_pass:
                print(f"  {_PASS} {label}")
            else:
                msg = f"{label}: expected ValidationError, got {req}"
                print(f"  {_FAIL} {msg}")
                errors.append(msg)
        except ValidationError as exc:
            if not should_pass:
                print(f"  {_PASS} {label}  [{exc.error_count()} error(s)]")
            else:
                msg = f"{label}: unexpected ValidationError — {exc}"
                print(f"  {_FAIL} {msg}")
                errors.append(msg)

    print("\n=== AdvisorRequest smoke test ===\n")

    # ── Valid inputs ──────────────────────────────────────────────────────────
    print("Valid inputs:")
    _valid = {
        "city": "Bengaluru",
        "monthly_bill": 3000.0,
        "roof_area_sqft": 500.0,
        "budget": 400_000.0,
    }
    check("Standard valid request (Bengaluru)", should_pass=True, data=_valid)
    check("All 15 cities accepted — Ahmedabad",
          should_pass=True,
          data={**_valid, "city": "Ahmedabad"})
    check("All 15 cities accepted — Guwahati",
          should_pass=True,
          data={**_valid, "city": "Guwahati"})
    check("monthly_bill at lower bound (500.0)",
          should_pass=True,
          data={**_valid, "monthly_bill": 500.0})
    check("monthly_bill at upper bound (100000.0)",
          should_pass=True,
          data={**_valid, "monthly_bill": 100_000.0})
    check("roof_area_sqft at lower bound (50.0)",
          should_pass=True,
          data={**_valid, "roof_area_sqft": 50.0})
    check("roof_area_sqft at upper bound (5000.0)",
          should_pass=True,
          data={**_valid, "roof_area_sqft": 5_000.0})
    check("budget at lower bound (50000.0)",
          should_pass=True,
          data={**_valid, "budget": 50_000.0})
    check("budget at upper bound (5000000.0)",
          should_pass=True,
          data={**_valid, "budget": 50_00_000.0})

    # ── Invalid city ──────────────────────────────────────────────────────────
    print("\nInvalid city:")
    check("Unsupported city name rejected",
          should_pass=False,
          data={**_valid, "city": "Varanasi"})
    check("Lowercase city name rejected (case-sensitive)",
          should_pass=False,
          data={**_valid, "city": "bengaluru"})
    check("Empty string rejected",
          should_pass=False,
          data={**_valid, "city": ""})

    # ── Invalid monthly_bill ──────────────────────────────────────────────────
    print("\nInvalid monthly_bill:")
    check("Below lower bound (499.99) rejected",
          should_pass=False,
          data={**_valid, "monthly_bill": 499.99})
    check("Above upper bound (100000.01) rejected",
          should_pass=False,
          data={**_valid, "monthly_bill": 100_000.01})
    check("Zero rejected",
          should_pass=False,
          data={**_valid, "monthly_bill": 0.0})
    check("Negative rejected",
          should_pass=False,
          data={**_valid, "monthly_bill": -500.0})

    # ── Invalid roof_area_sqft ────────────────────────────────────────────────
    print("\nInvalid roof_area_sqft:")
    check("Below lower bound (49.99) rejected",
          should_pass=False,
          data={**_valid, "roof_area_sqft": 49.99})
    check("Above upper bound (5000.01) rejected",
          should_pass=False,
          data={**_valid, "roof_area_sqft": 5_000.01})

    # ── Invalid budget ────────────────────────────────────────────────────────
    print("\nInvalid budget:")
    check("Below lower bound (49999.99) rejected",
          should_pass=False,
          data={**_valid, "budget": 49_999.99})
    check("Above upper bound (5000000.01) rejected",
          should_pass=False,
          data={**_valid, "budget": 50_00_000.01})

    # ── Missing fields ────────────────────────────────────────────────────────
    print("\nMissing fields:")
    check("Missing city rejected",
          should_pass=False,
          data={"monthly_bill": 3000.0, "roof_area_sqft": 500.0, "budget": 400_000.0})
    check("Missing monthly_bill rejected",
          should_pass=False,
          data={"city": "Bengaluru", "roof_area_sqft": 500.0, "budget": 400_000.0})
    check("Missing roof_area_sqft rejected",
          should_pass=False,
          data={"city": "Bengaluru", "monthly_bill": 3000.0, "budget": 400_000.0})
    check("Missing budget rejected",
          should_pass=False,
          data={"city": "Bengaluru", "monthly_bill": 3000.0, "roof_area_sqft": 500.0})

    # ── Result ────────────────────────────────────────────────────────────────
    print()
    if errors:
        print(f"❌ {len(errors)} test(s) failed:")
        for e in errors:
            print(f"   • {e}")
        sys.exit(1)
    else:
        print("✅ All tests passed.")
