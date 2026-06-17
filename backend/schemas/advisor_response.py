"""
backend/schemas/advisor_response.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PURPOSE
───────
Response contract for POST /advisor.

Represents the personalised investment outputs computed by AdvisorService
from NB12 formulas, joined with SDSF lookup values from NB11.

No business logic. No calculations. No service or data-layer imports.

ENDPOINT
────────
  POST /advisor

  Consumed by:
    - Results dashboard → Investment Analysis tab (primary)
    - Results dashboard → EconomicsVsSuitabilityPanel
      (suitability, reliability_score, prediction_confidence allow this
       panel to render from a single POST /advisor call)

FIELD SOURCES
─────────────
  city                       ← input echo (AdvisorRequest.city)
  city_slug                  ← derived: data_loader._make_slug(city)
  system_size_kw             ← NB12 §6 recommend_system_sizes() → Rec_kW
                               CSV: System_Size_kW
  annual_generation_kwh      ← NB12 §7 annual_generation()
                               CSV: Annual_Generation_kWh
  annual_savings             ← NB12 §8 Year-1 electricity savings (₹)
                               CSV: Annual_Savings
  payback_years              ← NB12 §8 net_cost / year1_savings
                               CSV: Payback_Years
  lifetime_savings           ← NB12 §8 25-year cumulative savings (₹)
                               CSV: Lifetime_Savings
  net_benefit_inr            ← NB12 §8 lifetime_savings − net_system_cost (₹)
                               CSV: Net_Benefit_INR
  investment_recommendation  ← NB12 §9 recommendation engine
                               CSV: Investment_Recommendation
  recommendation_explanation ← NB12 §10 REC_TEMPLATES output
                               CSV: Recommendation_Explanation
  suitability                ← SDSF CSV: Suitability (emoji stripped)
                               joined by AdvisorService
  reliability_score          ← SDSF CSV: Reliability Score
                               joined by AdvisorService
  prediction_confidence      ← SDSF CSV: Prediction Confidence
                               joined by AdvisorService

NOT INCLUDED (per approved schema plan):
  system_cost_gross, subsidy, system_cost_net — not in finalized NB12 outputs
  suitability_raw  — emoji rendering is a frontend concern
  limiting_factor, limiting_message — deferred
  SHAP fields — deferred pending shap_summary.csv

LOCATION
────────
  backend/schemas/advisor_response.py

DEPENDENCIES
────────────
  pydantic >= 2.0
  schemas.readiness_response — imports Suitability, PredictionConfidence
    to avoid redefining the same Literal types.
  No data-layer or service imports.

TESTING INSTRUCTIONS
────────────────────
  Run from the backend/ directory:

      python -m schemas.advisor_response

  Expected output: all construction, rejection, and round-trip cases pass.

  Key cases for Phase 5 integration tests:
    - All 3 investment_recommendation values accepted
    - "Not Recommended" accepted (valid NB12 engine output)
    - Unknown recommendation string rejected
    - suitability_raw as extra field rejected (extra="forbid")
    - Missing any required field raises ValidationError
    - JSON output contains no emoji in suitability field
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from schemas.readiness_response import PredictionConfidence, Suitability

# ─────────────────────────────────────────────────────────────────────────────
# Categorical literal
# Source: solar_investment_advisor_results.csv → Investment_Recommendation
# "Not Recommended" is defined in NB12 §9 engine but absent from the
# current 15-city dataset. Included so AdvisorService can return it for
# future cities without a schema change.
# ─────────────────────────────────────────────────────────────────────────────

InvestmentRecommendation = Literal[
    "Highly Recommended",
    "Recommended",
    "Consider Carefully",
    "Not Recommended",
]


# ─────────────────────────────────────────────────────────────────────────────
# Response schema
# ─────────────────────────────────────────────────────────────────────────────

class AdvisorResponse(BaseModel):
    """
    Personalised solar investment outputs for one user assessment.

    Returned by POST /advisor.
    NB12 financial outputs joined with NB11 SDSF lookup values.
    """

    # ── City identity ─────────────────────────────────────────────────────────

    city: str = Field(
        ...,
        description="City name, echoed from the request.",
        examples=["Bengaluru"],
    )

    city_slug: str = Field(
        ...,
        description=(
            "URL-safe slug for the city. "
            "Used by the frontend to navigate to /results/{city_slug}."
        ),
        examples=["bengaluru"],
    )

    # ── System output ─────────────────────────────────────────────────────────

    system_size_kw: float = Field(
        ...,
        ge=0,
        description=(
            "Recommended solar system size in kW, snapped to the nearest 0.5 kW. "
            "Source: NB12 §6 recommend_system_sizes() → Rec_kW."
        ),
        examples=[3.0],
    )

    annual_generation_kwh: int = Field(
        ...,
        ge=0,
        description=(
            "Estimated annual electricity generation in kWh. "
            "Formula: system_size_kw × mean_ghi × 365 × 0.78 (performance ratio). "
            "Source: NB12 §7."
        ),
        examples=[4503],
    )

    # ── Financial outputs ─────────────────────────────────────────────────────

    annual_savings: int = Field(
        ...,
        ge=0,
        description=(
            "Estimated Year-1 electricity savings in Indian Rupees (₹). "
            "Formula: annual_generation_kwh × ₹7.0/kWh (fixed tariff). "
            "Source: NB12 §8."
        ),
        examples=[31520],
    )

    payback_years: float = Field(
        ...,
        ge=0,
        description=(
            "Estimated payback period in years. "
            "Formula: net_system_cost / annual_savings. "
            "Source: NB12 §8."
        ),
        examples=[3.7],
    )

    lifetime_savings: int = Field(
        ...,
        ge=0,
        description=(
            "Estimated cumulative electricity savings over 25 years in ₹, "
            "accounting for 0.5%/year panel degradation and 4%/year tariff escalation. "
            "Source: NB12 §8."
        ),
        examples=[1224427],
    )

    net_benefit_inr: int = Field(
    ...,
    description=(
        "Net financial benefit over 25 years in ₹ "
        "(lifetime_savings minus net system cost after subsidy). "
        "Source: NB12 §8."
    ),
    examples=[1108927],
    )

    # ── Recommendation ────────────────────────────────────────────────────────

    investment_recommendation: InvestmentRecommendation = Field(
        ...,
        description=(
            "Investment recommendation from the NB12 §9 rule-based engine. "
            "Determined by suitability rank and payback period thresholds."
        ),
        examples=["Highly Recommended"],
    )

    recommendation_explanation: str = Field(
        ...,
        description=(
            "Plain-language investment rationale generated from NB12 §10 "
            "REC_TEMPLATES. Served verbatim — not rewritten by the backend."
        ),
        examples=[
            "Bengaluru is Highly Recommended for residential solar investment. "
            "The city exhibits strong solar resource availability (Mean GHI: "
            "5.27 kWh/m²/d), high climatic reliability (Reliability Score: "
            "81.1/100), and an estimated payback period of 3.7 years."
        ],
    )

    # ── SDSF context (joined from NB11) ───────────────────────────────────────
    # Included so the frontend EconomicsVsSuitabilityPanel can render from
    # a single POST /advisor response without a second GET /readiness call.

    suitability: Suitability = Field(
        ...,
        description=(
            "Solar resource suitability classification from SDSF (NB11). "
            "Emoji prefix stripped. "
            "Source: sdsf_city_dashboard.csv → Suitability (cleaned)."
        ),
        examples=["Highly Suitable"],
    )

    reliability_score: float = Field(
    ...,
    ge=0,
    le=100,
    description=(
        "Composite solar resource reliability score on a 0–100 scale (NB11 §3). "
        "Source: sdsf_city_dashboard.csv → Reliability Score."
    ),
    examples=[81.1],
    )

    prediction_confidence: PredictionConfidence = Field(
        ...,
        description=(
            "Model prediction confidence tier for this city (NB11 §4). "
            "Source: sdsf_city_dashboard.csv → Prediction Confidence."
        ),
        examples=["High"],
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "city": "Bengaluru",
                    "city_slug": "bengaluru",
                    "system_size_kw": 3.0,
                    "annual_generation_kwh": 4503,
                    "annual_savings": 31520,
                    "payback_years": 3.7,
                    "lifetime_savings": 1224427,
                    "net_benefit_inr": 1108927,
                    "investment_recommendation": "Highly Recommended",
                    "recommendation_explanation": (
                        "Bengaluru is Highly Recommended for residential solar "
                        "investment. The city exhibits strong solar resource "
                        "availability (Mean GHI: 5.27 kWh/m²/d), high climatic "
                        "reliability (Reliability Score: 81.1/100), and an "
                        "estimated payback period of 3.7 years."
                    ),
                    "suitability": "Highly Suitable",
                    "reliability_score": 81.1,
                    "prediction_confidence": "High",
                }
            ]
        },
    )


# ─────────────────────────────────────────────────────────────────────────────
# Smoke test (python -m schemas.advisor_response)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json
    import sys
    from pydantic import ValidationError

    _PASS = "✅"
    _FAIL = "❌"
    _errors: list[str] = []

    _valid: dict = {
        "city": "Bengaluru",
        "city_slug": "bengaluru",
        "system_size_kw": 3.0,
        "annual_generation_kwh": 4503,
        "annual_savings": 31520,
        "payback_years": 3.7,
        "lifetime_savings": 1224427,
        "net_benefit_inr": 1108927,
        "investment_recommendation": "Highly Recommended",
        "recommendation_explanation": (
            "Bengaluru is Highly Recommended for residential solar investment."
        ),
        "suitability": "Highly Suitable",
        "reliability_score": 81.1,
        "prediction_confidence": "High",
    }

    def check(label: str, should_pass: bool, data: dict) -> None:
        try:
            AdvisorResponse(**data)
            if should_pass:
                print(f"  {_PASS} {label}")
            else:
                msg = f"{label}: expected ValidationError, got valid model"
                print(f"  {_FAIL} {msg}")
                _errors.append(msg)
        except ValidationError as exc:
            if not should_pass:
                print(f"  {_PASS} {label}  [{exc.error_count()} error(s)]")
            else:
                msg = f"{label}: unexpected ValidationError — {exc}"
                print(f"  {_FAIL} {msg}")
                _errors.append(msg)

    print("\n=== AdvisorResponse smoke test ===\n")

    print("Valid construction:")
    check("Bengaluru canonical row", should_pass=True, data=_valid)

    for rec in ["Highly Recommended", "Recommended", "Consider Carefully",
                "Not Recommended"]:
        check(f"investment_recommendation='{rec}'", should_pass=True,
              data={**_valid, "investment_recommendation": rec})

    for suit in ["Highly Suitable", "Suitable", "Moderately Suitable"]:
        check(f"suitability='{suit}'", should_pass=True,
              data={**_valid, "suitability": suit})

    for conf in ["High", "Medium", "Low"]:
        check(f"prediction_confidence='{conf}'", should_pass=True,
              data={**_valid, "prediction_confidence": conf})

    print("\nInvalid recommendation:")
    check("Unknown recommendation rejected", should_pass=False,
          data={**_valid, "investment_recommendation": "Strong Buy"})
    check("Raw emoji suitability rejected", should_pass=False,
          data={**_valid, "suitability": "✅ Highly Suitable"})

    print("\nextra='forbid':")
    check("system_cost_gross rejected", should_pass=False,
          data={**_valid, "system_cost_gross": 165000})
    check("subsidy rejected", should_pass=False,
          data={**_valid, "subsidy": 49500})
    check("limiting_factor rejected", should_pass=False,
          data={**_valid, "limiting_factor": "roof"})
    check("suitability_raw rejected", should_pass=False,
          data={**_valid, "suitability_raw": "✅ Highly Suitable"})

    print("\nMissing required fields:")
    for field in _valid.keys():
        data = {k: v for k, v in _valid.items() if k != field}
        check(f"Missing '{field}' rejected", should_pass=False, data=data)

    print("\nJSON round-trip:")
    try:
        resp = AdvisorResponse(**_valid)
        serialised = resp.model_dump_json()
        parsed = json.loads(serialised)
        assert parsed["city"] == "Bengaluru"
        assert parsed["suitability"] == "Highly Suitable"
        assert "✅" not in parsed["suitability"]
        assert "suitability_raw" not in parsed
        assert "system_cost_gross" not in parsed
        assert "subsidy" not in parsed
        print(f"  {_PASS} Serialises correctly")
        print(f"  {_PASS} No emoji in suitability")
        print(f"  {_PASS} Excluded fields absent from output")
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
