"""
backend/services/advisor_service.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PURPOSE
───────
Core computation service for POST /advisor.

Orchestrates the complete NB12 personalised investment workflow:
consumption estimation → system sizing → financial analysis →
recommendation engine → explanation generation → AdvisorResponse.

This is the only service that performs live calculations.
All formula implementations are delegated to utils/calculations.py.
No formula is duplicated here.

RESPONSIBILITIES
────────────────
  Single public method:

    calculate(request: AdvisorRequest) → AdvisorResponse

  Steps (mirrors NB12 §5 – §10 exactly):
    1.  Resolve city name/slug → canonical name
    2.  Fetch SDSFRow (GHI, suitability_rank, reliability_score, etc.)
    3.  estimate_consumption()        → monthly_kwh, annual_kwh
    4.  recommend_system_sizes()      → {Min_kW, Rec_kW, Max_kW, Roof_m2}
    5.  annual_generation(Rec_kW)     → gen_kwh
    6.  net_cost(Rec_kW)              → net_cost_inr
    7.  budget_adequate               → budget >= net_cost_inr
    8.  lifetime_savings_series()     → sum → lifetime_inr
    9.  simple_payback()              → payback_years
    10. net_benefit_inr               → lifetime_inr - net_cost_inr
    11. investment_recommendation()   → (rec_str, rationale_code)
    12. _generate_explanation()       → explanation_str
    13. Construct AdvisorResponse with joined SDSF context fields

WHAT THIS SERVICE DOES NOT DO
──────────────────────────────
  ✗ Re-implement any formula from calculations.py
  ✗ Read CSV files directly
  ✗ Use pandas
  ✗ Define FastAPI routes
  ✗ Serialise responses
  ✗ Recalculate SDSF outputs (served from DataLoader as frozen values)
  ✗ Accept tariff as a user input (fixed at TARIFF = ₹7.0/kWh)

LOCATION
────────
  backend/services/advisor_service.py

DEPENDENCIES
────────────
  data.data_loader          — loader singleton
  utils.calculations        — all 7 calculation functions
  utils.constants           — TARIFF (fixed system constant)
  utils.exceptions          — CityNotFoundError, CalculationError
  schemas.advisor_request   — AdvisorRequest
  schemas.advisor_response  — AdvisorResponse

EXPLANATION TEMPLATES
─────────────────────
  REC_TEMPLATES is sourced verbatim from NB12 §10, Cell 22.
  generate_explanation() was deliberately excluded from calculations.py
  (text rendering, not numerical calculation) and is implemented here
  as a private module-level function _generate_explanation().
  The template strings and format keys are preserved exactly as written
  in the notebook. No text has been modified.

ERROR HANDLING
──────────────
  CityNotFoundError     — loader.resolve_city() raises KeyError; caught
                          here and re-raised as CityNotFoundError.
                          Route handler → HTTP 404.

  CalculationError      — raised if payback_years is infinite (zero
                          year-1 savings, which cannot occur with
                          validated inputs but is guarded defensively).
                          Route handler → HTTP 500.

  DataLoaderError       — raised by loader._assert_loaded() if startup
                          did not call load(). Not caught here.
                          Route handler → HTTP 500.

TESTING INSTRUCTIONS
────────────────────
  Run from the backend/ directory:

      python -m services.advisor_service

  Expected output: all cases pass.

  Key cases for Phase 5 integration tests:
    - Standard profile (₹3,000/month, 500 sqft, ₹400,000) matches
      the pre-computed CSV values for each city (within rounding)
    - Invalid city raises CityNotFoundError
    - Budget exactly equal to net_cost → budget_adequate=True
    - Budget one rupee below net_cost → budget_adequate=False
    - Very small roof (50 sqft) clamps to MIN_SYS_KW (1.0 kW)
    - Very large budget / roof → capped at MAX_PHASE1_KW (10.0 kW)
    - All 15 cities return a valid AdvisorResponse
"""

from __future__ import annotations

import logging
import math

from data.data_loader import loader
from schemas.advisor_request import AdvisorRequest
from schemas.advisor_response import AdvisorResponse
from utils.calculations import (
    annual_generation,
    estimate_consumption,
    investment_recommendation,
    lifetime_savings_series,
    net_cost,
    recommend_system_sizes,
    simple_payback,
)
from utils.constants import TARIFF
from utils.exceptions import CalculationError, CityNotFoundError

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Explanation templates
# Source: NB12 §10, Cell 22 — preserved verbatim.
# generate_explanation() was deliberately excluded from calculations.py
# (text rendering, not numerical). Implemented here as a private helper.
# Template strings and format keys are byte-for-byte identical to the notebook.
# ─────────────────────────────────────────────────────────────────────────────

_REC_TEMPLATES: dict[str, str] = {
    "Highly Recommended": (
        "{city} is Highly Recommended for residential solar investment. "
        "The city exhibits strong solar resource availability (Mean GHI: {ghi:.2f} kWh/m²/d), "
        "high climatic reliability (Reliability Score: {rs:.1f}/100), "
        "and an estimated payback period of {payback:.1f} years — well below the 7-year threshold "
        "for strong ROI. The recommended {kw:.1f} kW system is expected to generate {gen:,} kWh/year, "
        "saving ₹{yr1:,} in the first year and ₹{lifetime:,} over 25 years."
    ),
    "Recommended": (
        "{city} is Recommended for residential solar investment. "
        "Solar resource availability is good (Mean GHI: {ghi:.2f} kWh/m²/d) "
        "with a reliability score of {rs:.1f}/100. "
        "The estimated payback period of {payback:.1f} years is within acceptable bounds. "
        "A {kw:.1f} kW system is recommended, projecting {gen:,} kWh/year in generation "
        "and ₹{lifetime:,} in lifetime savings."
    ),
    "Consider Carefully": (
        "{city} warrants Careful Consideration before committing to solar investment. "
        "While solar resource suitability is rated '{suit}', the estimated payback period "
        "of {payback:.1f} years is longer than optimal, possibly reflecting lower GHI "
        "({ghi:.2f} kWh/m²/d) or higher system costs relative to consumption. "
        "A {kw:.1f} kW system is feasible, but the homeowner should verify the latest tariff "
        "rates and explore available subsidies before proceeding."
    ),
    "Not Recommended": (
        "{city} is Not Recommended for residential solar investment at this time. "
        "The combination of solar resource suitability ('{suit}') and a projected payback "
        "period of {payback:.1f} years makes the investment financially unattractive "
        "over a 25-year system lifetime. The homeowner should reconsider if tariffs increase "
        "substantially or if system costs decline."
    ),
}


def _generate_explanation(
    city: str,
    rec: str,
    suit: str,
    ghi: float,
    rs: float,
    payback: float,
    kw: float,
    gen: int,
    yr1: int,
    lifetime: int,
) -> str:
    """
    Generate a plain-language investment explanation.

    Source: NB12 §10, Cell 22 — generate_explanation() function body,
    preserved verbatim. The only structural change is removing the
    unused `profile_name` parameter (the notebook passed it but never
    used it inside the template string).

    Parameters mirror the template format-key names exactly.
    """
    template = _REC_TEMPLATES[rec]
    return template.format(
        city=city,
        suit=suit,
        ghi=ghi,
        rs=rs,
        payback=payback,
        kw=kw,
        gen=gen,
        yr1=yr1,
        lifetime=lifetime,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Service
# ─────────────────────────────────────────────────────────────────────────────

class AdvisorService:
    """
    Personalised solar investment advisor.

    Stateless — holds no mutable data of its own.
    Safe to instantiate once at startup and reuse across requests.
    """

    def calculate(self, request: AdvisorRequest) -> AdvisorResponse:
        """
        Run the complete NB12 investment workflow for one user request.

        Parameters
        ----------
        request : AdvisorRequest
            Validated user inputs (city, monthly_bill, roof_area_sqft, budget).
            Tariff is not in the request — fixed at TARIFF = ₹7.0/kWh.

        Returns
        -------
        AdvisorResponse
            Complete personalised investment outputs joined with SDSF context.

        Raises
        ------
        CityNotFoundError
            If request.city does not resolve to a supported city.
        CalculationError
            If year-1 savings are zero or negative (defensive guard;
            cannot occur with validated inputs under normal conditions).
        DataLoaderError
            If DataLoader.load() was not called at startup.
        """

        # ── Step 1: Resolve city ──────────────────────────────────────────────
        try:
            canonical = loader.resolve_city(request.city)
        except KeyError:
            raise CityNotFoundError(
                f"City not supported: {repr(request.city)}. "
                f"Supported cities: {loader.city_list()}"
            )

        # ── Step 2: Fetch SDSFRow ─────────────────────────────────────────────
        row = loader.get_sdsf_row(canonical)

        logger.debug(
            "[advisor_service] Processing request for '%s' "
            "(bill=%.0f, roof=%.0f sqft, budget=%.0f).",
            canonical, request.monthly_bill, request.roof_area_sqft, request.budget,
        )

        # ── Step 3: Estimate consumption ─────────────────────────────────────
        _monthly_kwh, annual_kwh = estimate_consumption(
            monthly_bill_inr=request.monthly_bill,
            tariff_inr_kwh=TARIFF,
        )

        # ── Step 4: Recommend system size ─────────────────────────────────────
        sizes = recommend_system_sizes(
            annual_kwh=annual_kwh,
            roof_sqft=request.roof_area_sqft,
            budget_inr=request.budget,
            mean_ghi=row.mean_ghi,
            p10_ghi=row.p10_ghi,
        )
        rec_kw: float = sizes["Rec_kW"]

        # ── Step 5: Annual generation ─────────────────────────────────────────
        gen_kwh_float = annual_generation(system_kw=rec_kw, ghi=row.mean_ghi)
        gen_kwh: int = round(gen_kwh_float)

        # ── Step 6: Net system cost ───────────────────────────────────────────
        net_cost_inr: float = net_cost(system_kw=rec_kw)

        # ── Step 7: Budget adequacy ───────────────────────────────────────────
        budget_adequate: bool = request.budget >= net_cost_inr

        # ── Step 8: Lifetime savings ──────────────────────────────────────────
        year1_savings: float = gen_kwh_float * TARIFF
        series = lifetime_savings_series(
            annual_gen_kwh=gen_kwh_float,
            tariff=TARIFF,
        )
        lifetime_inr: int = round(sum(series))

        # ── Step 9: Payback ───────────────────────────────────────────────────
        payback: float = simple_payback(
            net_cost_inr=net_cost_inr,
            year1_savings=year1_savings,
        )

        # Defensive guard: infinite payback cannot occur with validated inputs
        # (monthly_bill >= 500 guarantees year1_savings > 0), but guard
        # explicitly so CalculationError propagates cleanly if it ever does.
        if math.isinf(payback):
            raise CalculationError(
                f"Payback calculation produced infinity for city={canonical!r}, "
                f"rec_kw={rec_kw}, year1_savings={year1_savings:.2f}. "
                "This indicates zero annual savings — check tariff and GHI values."
            )

        payback_rounded: float = round(payback, 1)

        # ── Step 10: Net benefit ──────────────────────────────────────────────
        net_benefit: int = round(lifetime_inr - net_cost_inr)

        # ── Step 11: Investment recommendation ───────────────────────────────
        rec_str, _rationale_code = investment_recommendation(
            suitability_rank=row.suitability_rank,
            payback_years=payback_rounded,
            budget_adequate=budget_adequate,
        )

        # ── Step 12: Generate explanation ─────────────────────────────────────
        explanation = _generate_explanation(
            city=canonical,
            rec=rec_str,
            suit=row.suitability,           # clean label, no emoji
            ghi=row.mean_ghi,
            rs=row.reliability_score,
            payback=payback_rounded,
            kw=rec_kw,
            gen=gen_kwh,
            yr1=round(year1_savings),
            lifetime=lifetime_inr,
        )

        logger.debug(
            "[advisor_service] Result for '%s': rec=%r, payback=%.1f yrs, "
            "system=%.1f kW, lifetime=₹%d.",
            canonical, rec_str, payback_rounded, rec_kw, lifetime_inr,
        )

        # ── Step 13: Construct AdvisorResponse ───────────────────────────────
        return AdvisorResponse(
            city=row.city,
            city_slug=row.city_slug,
            system_size_kw=rec_kw,
            annual_generation_kwh=gen_kwh,
            annual_savings=round(year1_savings),
            payback_years=payback_rounded,
            lifetime_savings=lifetime_inr,
            net_benefit_inr=net_benefit,
            investment_recommendation=rec_str,
            recommendation_explanation=explanation,
            # SDSF context — joined from SDSFRow so the frontend
            # EconomicsVsSuitabilityPanel renders from a single response
            suitability=row.suitability,
            reliability_score=row.reliability_score,
            prediction_confidence=row.prediction_confidence,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Module-level singleton
# Imported by the route handler:
#
#     from services.advisor_service import advisor_service
# ─────────────────────────────────────────────────────────────────────────────

advisor_service = AdvisorService()


# ─────────────────────────────────────────────────────────────────────────────
# Smoke test (python -m services.advisor_service)
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
    loader.load(
        os.path.join(_data_dir, "sdsf_city_dashboard.csv"),
        os.path.join(_data_dir, "solar_investment_advisor_results.csv"),
    )

    svc = AdvisorService()

    # Standard profile used to generate the pre-computed CSV — outputs
    # should match those CSV values within rounding tolerance.
    _STANDARD = AdvisorRequest(
        city="Bengaluru",
        monthly_bill=3000.0,
        roof_area_sqft=500.0,
        budget=400_000.0,
    )

    print("\n=== AdvisorService smoke test ===\n")

    # ── Valid standard request ────────────────────────────────────────────────
    print("Standard profile (Bengaluru, ₹3k bill, 500 sqft, ₹400k budget):")
    try:
        resp = svc.calculate(_STANDARD)

        if isinstance(resp, AdvisorResponse):
            ok("Returns AdvisorResponse")
        else:
            fail(f"Expected AdvisorResponse, got {type(resp)}")

        # These values are known from the exported CSV for the standard profile
        _expected = {
            "city":                     "Bengaluru",
            "city_slug":                "bengaluru",
            "system_size_kw":           3.0,
            "annual_generation_kwh":    4503,
            "annual_savings":           31520,
            "payback_years":            3.7,
            "lifetime_savings":         1224427,
            "investment_recommendation":"Highly Recommended",
            "suitability":              "Highly Suitable",
            "prediction_confidence":    "High",
        }

        field_errors = []
        for field, expected_val in _expected.items():
            actual_val = getattr(resp, field)
            # Allow ±1 on integer financial fields, ±0.1 on floats
            if isinstance(expected_val, int):
                if abs(actual_val - expected_val) > 1:
                    field_errors.append(
                        f"  {field}: expected {expected_val}, got {actual_val}"
                    )
            elif isinstance(expected_val, float):
                if abs(actual_val - expected_val) > 0.1:
                    field_errors.append(
                        f"  {field}: expected {expected_val}, got {actual_val}"
                    )
            else:
                if actual_val != expected_val:
                    field_errors.append(
                        f"  {field}: expected {expected_val!r}, got {actual_val!r}"
                    )

        if field_errors:
            for e in field_errors:
                fail(e)
        else:
            ok("All field values match pre-computed CSV within rounding tolerance")

        # Confirm no emoji in suitability
        if "✅" not in resp.suitability and "👍" not in resp.suitability:
            ok("suitability has no emoji")
        else:
            fail(f"Emoji in suitability: {resp.suitability!r}")

        # Confirm explanation is non-trivially long and contains city name
        if len(resp.recommendation_explanation) > 100 and "Bengaluru" in resp.recommendation_explanation:
            ok("recommendation_explanation is substantive and contains city name")
        else:
            fail(f"Explanation suspicious: {resp.recommendation_explanation[:80]!r}")

        # Confirm net_benefit_inr = lifetime_savings - net_cost (approx)
        from utils.calculations import net_cost as _net_cost
        _nc = _net_cost(resp.system_size_kw)
        _expected_nb = round(resp.lifetime_savings - _nc)
        if abs(resp.net_benefit_inr - _expected_nb) <= 1:
            ok("net_benefit_inr = lifetime_savings − net_cost (within ±1 ₹)")
        else:
            fail(
                f"net_benefit_inr mismatch: got {resp.net_benefit_inr}, "
                f"expected ~{_expected_nb}"
            )

    except Exception as exc:
        fail(f"calculate(_STANDARD) raised {type(exc).__name__}: {exc}")

    # ── All 15 cities with standard profile ───────────────────────────────────
    print("\nAll 15 cities (standard profile):")
    _cities = ["Ahmedabad","Bengaluru","Bhopal","Bhubaneswar","Chandigarh",
               "Chennai","Delhi","Guwahati","Hyderabad","Jaipur",
               "Kochi","Kolkata","Mangalore","Mumbai","Pune"]
    city_errors = []
    for city_name in _cities:
        try:
            r = svc.calculate(AdvisorRequest(
                city=city_name,
                monthly_bill=3000.0,
                roof_area_sqft=500.0,
                budget=400_000.0,
            ))
            assert isinstance(r, AdvisorResponse), "not AdvisorResponse"
            assert r.city == city_name
            assert r.system_size_kw >= 1.0
            assert r.annual_generation_kwh > 0
            assert r.annual_savings > 0
            assert r.payback_years > 0
            assert not math.isinf(r.payback_years)
            assert r.lifetime_savings > 0
            assert r.investment_recommendation in {
                "Highly Recommended", "Recommended",
                "Consider Carefully", "Not Recommended",
            }
            assert len(r.recommendation_explanation) > 50
            assert "✅" not in r.suitability
        except Exception as exc:
            city_errors.append(f"{city_name}: {exc}")
    if city_errors:
        for e in city_errors:
            fail(e)
    else:
        ok("All 15 cities return valid AdvisorResponse")

    # ── City slug input resolves correctly ────────────────────────────────────
    print("\nCity slug resolution:")
    try:
        resp_slug = svc.calculate(AdvisorRequest(
            city="Bengaluru",   # canonical name (Literal enforces this in schema)
            monthly_bill=3000.0,
            roof_area_sqft=500.0,
            budget=400_000.0,
        ))
        if resp_slug.city_slug == "bengaluru":
            ok("city_slug correctly set to 'bengaluru'")
        else:
            fail(f"Wrong city_slug: {resp_slug.city_slug!r}")
    except Exception as exc:
        fail(f"Raised {type(exc).__name__}: {exc}")

    # ── Invalid city raises CityNotFoundError ─────────────────────────────────
    print("\nInvalid city handling:")
    # Note: AdvisorRequest.city is a Literal — invalid city names are
    # rejected by Pydantic before reaching AdvisorService. We test the
    # service-level guard via resolve_city directly by temporarily
    # constructing a valid request and patching the city attribute.
    # In practice this code path is reached if the Literal set is ever
    # expanded inconsistently with the CSVs.
    try:
        valid_req = AdvisorRequest(
            city="Bengaluru",
            monthly_bill=3000.0,
            roof_area_sqft=500.0,
            budget=400_000.0,
        )
        # Bypass Pydantic's frozen model by constructing a plain object
        class _FakeRequest:
            city = "Varanasi"
            monthly_bill = 3000.0
            roof_area_sqft = 500.0
            budget = 400_000.0

        svc.calculate(_FakeRequest())  # type: ignore[arg-type]
        fail("Expected CityNotFoundError for unsupported city")
    except CityNotFoundError:
        ok("Unsupported city raises CityNotFoundError")
    except Exception as exc:
        fail(f"Wrong exception type: {type(exc).__name__}: {exc}")

    # ── Small roof clamps to MIN_SYS_KW ──────────────────────────────────────
    print("\nBoundary inputs:")
    try:
        resp_small = svc.calculate(AdvisorRequest(
            city="Bengaluru",
            monthly_bill=500.0,     # minimum bill
            roof_area_sqft=50.0,    # minimum roof
            budget=50_000.0,        # minimum budget
        ))
        from utils.constants import MIN_SYS_KW
        if resp_small.system_size_kw >= MIN_SYS_KW:
            ok(f"Minimum inputs → system_size_kw >= MIN_SYS_KW ({MIN_SYS_KW} kW)")
        else:
            fail(f"system_size_kw {resp_small.system_size_kw} < MIN_SYS_KW {MIN_SYS_KW}")
    except Exception as exc:
        fail(f"Minimum inputs raised {type(exc).__name__}: {exc}")

    try:
        from utils.constants import MAX_PHASE1_KW
        resp_large = svc.calculate(AdvisorRequest(
            city="Chennai",
            monthly_bill=100_000.0,  # maximum bill
            roof_area_sqft=5_000.0,  # maximum roof
            budget=50_00_000.0,      # maximum budget
        ))
        if resp_large.system_size_kw <= MAX_PHASE1_KW:
            ok(f"Maximum inputs → system_size_kw <= MAX_PHASE1_KW ({MAX_PHASE1_KW} kW)")
        else:
            fail(f"system_size_kw {resp_large.system_size_kw} > MAX_PHASE1_KW {MAX_PHASE1_KW}")
    except Exception as exc:
        fail(f"Maximum inputs raised {type(exc).__name__}: {exc}")

    # ── Schema contract: no extra fields ─────────────────────────────────────
    print("\nSchema contract:")
    import json
    try:
        resp_json = json.loads(resp.model_dump_json())
        forbidden = {"system_cost_gross", "subsidy", "system_cost_net",
                     "suitability_raw", "limiting_factor"}
        present = forbidden & set(resp_json.keys())
        if not present:
            ok("No forbidden fields in response JSON")
        else:
            fail(f"Forbidden fields present: {present}")

        required = {"city", "city_slug", "system_size_kw", "annual_generation_kwh",
                    "annual_savings", "payback_years", "lifetime_savings",
                    "net_benefit_inr", "investment_recommendation",
                    "recommendation_explanation", "suitability",
                    "reliability_score", "prediction_confidence"}
        missing = required - set(resp_json.keys())
        if not missing:
            ok("All required fields present in response JSON")
        else:
            fail(f"Missing required fields: {missing}")
    except Exception as exc:
        fail(f"JSON schema check failed: {exc}")

    # ── Singleton ─────────────────────────────────────────────────────────────
    print("\nSingleton:")
    if isinstance(advisor_service, AdvisorService):
        ok("Module-level advisor_service is an AdvisorService instance")
    else:
        fail(f"Expected AdvisorService, got {type(advisor_service)}")

    singleton_resp = advisor_service.calculate(_STANDARD)
    if singleton_resp.city == "Bengaluru":
        ok("Singleton calculate() returns correct city")
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
