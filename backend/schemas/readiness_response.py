"""
backend/schemas/readiness_response.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PURPOSE
───────
Response contract for GET /readiness/{city}.

Represents the complete output of the Solar Decision Support Framework
(Notebook 11) for one city. Every field maps directly to a column in
sdsf_city_dashboard.csv or to a deterministic derivation of one
(city_slug).

No business logic. No calculations. No service or data-layer imports.

ENDPOINT
────────
  GET /readiness/{city}

  Consumed by:
    - Results dashboard → Solar Readiness tab
    - Results dashboard → EconomicsVsSuitabilityPanel (suitability panel)

FIELD SOURCES
─────────────
  city               ← CSV: City
  city_slug          ← derived: data_loader._make_slug(City)
  mean_ghi           ← CSV: Mean GHI (kWh/m²/d)
  p10_ghi            ← CSV: P10 GHI
  p50_ghi            ← CSV: P50 GHI
  p90_ghi            ← CSV: P90 GHI
  reliability_score  ← CSV: Reliability Score
  rs_category        ← CSV: RS Category
  model_rmse         ← CSV: Model RMSE
  model_mape         ← CSV: Model MAPE (%)
  prediction_confidence ← CSV: Prediction Confidence
  suitability        ← CSV: Suitability (emoji prefix stripped)
  explanation        ← CSV: Explanation

LOCATION
────────
  backend/schemas/readiness_response.py

DEPENDENCIES
────────────
  pydantic >= 2.0   (BaseModel, Field, ConfigDict, Literal)
  No internal imports.

TESTING INSTRUCTIONS
────────────────────
  Run from the backend/ directory:

      python -m schemas.readiness_response

  Expected output: all construction and rejection cases pass.

  Key cases for integration tests (Phase 5):
    - Valid response round-trips through JSON serialisation
    - Unknown rs_category value raises ValidationError
    - Unknown prediction_confidence value raises ValidationError
    - Unknown suitability value raises ValidationError
    - Extra field raises ValidationError (extra="forbid")
    - All numeric fields accept float values in observed CSV ranges
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# ─────────────────────────────────────────────────────────────────────────────
# Categorical literals
# Values sourced directly from sdsf_city_dashboard.csv — verified against
# the real CSV. Extend only when the upstream notebook produces new values.
# ─────────────────────────────────────────────────────────────────────────────

RSCategory = Literal[
    "Consistent Producer",
    "Seasonal Producer",
    # Future categories defined in NB11 (not present in current 15-city data):
    # "Monsoon Sensitive",
    # "Highly Variable",
]

PredictionConfidence = Literal["High", "Medium", "Low"]

Suitability = Literal[
    "Highly Suitable",       # CSV: ✅ Highly Suitable
    "Suitable",              # CSV: 👍 Suitable
    "Moderately Suitable",   # CSV: ⚠️ Moderately Suitable
    # Future category defined in NB11 (not present in current 15-city data):
    # "Less Suitable",       # CSV: ❌ Less Suitable
]


# ─────────────────────────────────────────────────────────────────────────────
# Response schema
# ─────────────────────────────────────────────────────────────────────────────

class ReadinessResponse(BaseModel):
    """
    Solar Decision Support Framework (NB11) outputs for one city.

    Returned by GET /readiness/{city}.
    All fields are frozen research outputs — never recomputed by the backend.
    """


    # ── City identity ─────────────────────────────────────────────────────────

    city: str = Field(
        ...,
        description="City name, exactly as it appears in sdsf_city_dashboard.csv.",
        examples=["Bengaluru"],
    )

    city_slug: str = Field(
        ...,
        description=(
            "URL-safe slug derived from the city name. "
            "Used by the frontend to construct /results/{city_slug} routes."
        ),
        examples=["bengaluru"],
    )

    # ── Solar irradiance ──────────────────────────────────────────────────────

    mean_ghi: float = Field(
        ...,
        description=(
            "Annual mean predicted Global Horizontal Irradiance (GHI) "
            "in kWh/m²/day. Source: CSV column 'Mean GHI (kWh/m²/d)'."
        ),
        examples=[5.272],
    )

    p10_ghi: float = Field(
        ...,
        description=(
            "10th-percentile predicted GHI in kWh/m²/day. "
            "Conservative scenario — used for minimum system sizing. "
            "Source: CSV column 'P10 GHI'."
        ),
        examples=[3.58],
    )

    p50_ghi: float = Field(
        ...,
        description=(
            "Median predicted GHI in kWh/m²/day. "
            "Base-case scenario. "
            "Source: CSV column 'P50 GHI'."
        ),
        examples=[5.37],
    )

    p90_ghi: float = Field(
        ...,
        description=(
            "90th-percentile predicted GHI in kWh/m²/day. "
            "Optimistic scenario. "
            "Source: CSV column 'P90 GHI'."
        ),
        examples=[6.88],
    )

    # ── Reliability ───────────────────────────────────────────────────────────

    reliability_score: float = Field(
        ...,
        ge=0,
        le=100,
        description=(
            "Composite solar resource reliability score on a 0–100 scale..."
        ),
        examples=[81.1],
    )

    rs_category: RSCategory = Field(
        ...,
        description=(
            "Reliability Score category label. "
            "Consistent Producer ≥ 70, Seasonal Producer 50–69. "
            "Source: CSV column 'RS Category'."
        ),
        examples=["Consistent Producer"],
    )

    # ── Model accuracy ────────────────────────────────────────────────────────

    model_rmse: float = Field(
        ...,
        description=(
            "City-level XGBoost model Root Mean Squared Error (kWh/m²/day). "
            "Source: CSV column 'Model RMSE'."
        ),
        examples=[1.5739],
    )

    model_mape: float = Field(
        ...,
        description=(
            "City-level XGBoost model Mean Absolute Percentage Error (%). "
            "Source: CSV column 'Model MAPE (%)'."
        ),
        examples=[24.3],
    )

    # ── Prediction confidence and suitability ─────────────────────────────────

    prediction_confidence: PredictionConfidence = Field(
        ...,
        description=(
            "Model prediction confidence tier for this city, derived from "
            "RMSE and MAPE thresholds in NB11 §4. "
            "Source: CSV column 'Prediction Confidence'."
        ),
        examples=["High"],
    )

    suitability: Suitability = Field(
        ...,
        description=(
            "Solar resource suitability classification from the SDSF composite "
            "logic (NB11 §5). Emoji prefix stripped for API responses — "
            "rendering is a frontend concern. "
            "Source: CSV column 'Suitability' (cleaned)."
        ),
        examples=["Highly Suitable"],
    )

    # ── Explanation ───────────────────────────────────────────────────────────

    explanation: str = Field(
        ...,
        description=(
            "Plain-language suitability rationale generated programmatically "
            "in NB11. Served verbatim — not rewritten by the backend. "
            "Source: CSV column 'Explanation'."
        ),
        examples=[
            "Good solar resource availability, high climatic reliability, "
            "high prediction confidence."
        ],
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "city": "Bengaluru",
                    "city_slug": "bengaluru",
                    "mean_ghi": 5.272,
                    "p10_ghi": 3.58,
                    "p50_ghi": 5.37,
                    "p90_ghi": 6.88,
                    "reliability_score": 81.1,
                    "rs_category": "Consistent Producer",
                    "model_rmse": 1.5739,
                    "model_mape": 24.3,
                    "prediction_confidence": "High",
                    "suitability": "Highly Suitable",
                    "explanation": (
                        "Good solar resource availability, high climatic "
                        "reliability, high prediction confidence."
                    ),
                }
            ]
        },
    )


# ─────────────────────────────────────────────────────────────────────────────
# Smoke test (python -m schemas.readiness_response)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json
    import sys
    from pydantic import ValidationError

    _PASS = "✅"
    _FAIL = "❌"
    _errors: list[str] = []

    # Canonical valid payload — Bengaluru row from sdsf_city_dashboard.csv
    _valid: dict = {
        "city": "Bengaluru",
        "city_slug": "bengaluru",
        "mean_ghi": 5.272,
        "p10_ghi": 3.58,
        "p50_ghi": 5.37,
        "p90_ghi": 6.88,
        "reliability_score": 81.1,
        "rs_category": "Consistent Producer",
        "model_rmse": 1.5739,
        "model_mape": 24.3,
        "prediction_confidence": "High",
        "suitability": "Highly Suitable",
        "explanation": (
            "Good solar resource availability, high climatic reliability, "
            "high prediction confidence."
        ),
    }

    def check(label: str, should_pass: bool, data: dict) -> None:
        try:
            resp = ReadinessResponse(**data)
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

    print("\n=== ReadinessResponse smoke test ===\n")

    # ── Valid construction ────────────────────────────────────────────────────
    print("Valid construction:")
    check("Bengaluru canonical row", should_pass=True, data=_valid)

    # All 3 suitability values
    for suit in ["Highly Suitable", "Suitable", "Moderately Suitable"]:
        check(f"suitability='{suit}'", should_pass=True,
              data={**_valid, "suitability": suit})

    # All 2 rs_category values
    for cat in ["Consistent Producer", "Seasonal Producer"]:
        check(f"rs_category='{cat}'", should_pass=True,
              data={**_valid, "rs_category": cat})

    # All 3 prediction_confidence values
    for conf in ["High", "Medium", "Low"]:
        check(f"prediction_confidence='{conf}'", should_pass=True,
              data={**_valid, "prediction_confidence": conf})

    # Numeric edge values from CSV observed ranges
    check("mean_ghi at CSV min (4.297)", should_pass=True,
          data={**_valid, "mean_ghi": 4.297})
    check("mean_ghi at CSV max (5.285)", should_pass=True,
          data={**_valid, "mean_ghi": 5.285})
    check("reliability_score at CSV min (65.2)", should_pass=True,
          data={**_valid, "reliability_score": 65.2})
    check("reliability_score at CSV max (81.4)", should_pass=True,
          data={**_valid, "reliability_score": 81.4})

    # ── Invalid categoricals ──────────────────────────────────────────────────
    print("\nInvalid categoricals:")
    check("Unknown suitability value rejected",
          should_pass=False,
          data={**_valid, "suitability": "✅ Highly Suitable"})  # raw with emoji
    check("Unknown suitability — 'Excellent' rejected",
          should_pass=False,
          data={**_valid, "suitability": "Excellent"})
    check("Unknown rs_category rejected",
          should_pass=False,
          data={**_valid, "rs_category": "High Producer"})
    check("Unknown prediction_confidence rejected",
          should_pass=False,
          data={**_valid, "prediction_confidence": "Very High"})
    check("Lowercase prediction_confidence rejected",
          should_pass=False,
          data={**_valid, "prediction_confidence": "high"})

    # ── extra="forbid" ────────────────────────────────────────────────────────
    print("\nextra='forbid':")
    check("Extra field rejected",
          should_pass=False,
          data={**_valid, "suitability_raw": "✅ Highly Suitable"})
    check("SHAP field rejected",
          should_pass=False,
          data={**_valid, "top_shap_feature": "Cloud Cover"})
    check("Investment field rejected",
          should_pass=False,
          data={**_valid, "payback_years": 3.7})

    # ── Missing fields ────────────────────────────────────────────────────────
    print("\nMissing required fields:")
    for field in ["city", "city_slug", "mean_ghi", "p10_ghi", "p50_ghi",
                  "p90_ghi", "reliability_score", "rs_category", "model_rmse",
                  "model_mape", "prediction_confidence", "suitability",
                  "explanation"]:
        data = {k: v for k, v in _valid.items() if k != field}
        check(f"Missing '{field}' rejected", should_pass=False, data=data)

    # ── JSON round-trip ───────────────────────────────────────────────────────
    print("\nJSON round-trip:")
    try:
        resp = ReadinessResponse(**_valid)
        serialised = resp.model_dump_json()
        parsed = json.loads(serialised)
        assert parsed["city"] == "Bengaluru"
        assert parsed["suitability"] == "Highly Suitable"
        assert "suitability_raw" not in parsed
        assert parsed["mean_ghi"] == 5.272
        print(f"  {_PASS} Serialises and deserialises correctly")
        print(f"  {_PASS} 'suitability_raw' absent from serialised output")
    except Exception as exc:
        msg = f"JSON round-trip failed: {exc}"
        print(f"  {_FAIL} {msg}")
        _errors.append(msg)

    # ── Result ────────────────────────────────────────────────────────────────
    print()
    if _errors:
        print(f"❌ {len(_errors)} test(s) failed:")
        for e in _errors:
            print(f"   • {e}")
        sys.exit(1)
    else:
        print("✅ All tests passed.")
