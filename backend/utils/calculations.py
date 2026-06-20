"""
backend/utils/calculations.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PURPOSE
───────
Pure, deterministic calculation functions for the live recomputation path
(AdvisorService / POST /advisor). Every function below is extracted from
Notebook 12 — Residential Solar Investment Advisor — with formulas
preserved exactly as written in the notebook.

SOURCE NOTEBOOK
───────────────
  Notebook 12 — Residential Solar Investment Advisor
    §5  Monthly Consumption Estimation     (Cell 12) → estimate_consumption
    §6  System Size Recommendation Engine  (Cell 14) → recommend_system_sizes
    §7  Annual Energy Generation           (Cell 16) → annual_generation
    §8  Financial Analysis                 (Cell 18) → calc_subsidy,
                                                        net_cost,
                                                        lifetime_savings_series,
                                                        simple_payback
    §9  Investment Recommendation Engine   (Cell 20) → investment_recommendation

FUNCTIONS DELIBERATELY NOT EXTRACTED HERE (per extraction audit)
──────────────────────────────────────────────────────────────
  generate_explanation()   NB12 §10, Cell 22 — text/template rendering,
                            not numerical calculation. Belongs in a
                            presentation/explanations module, not here.
  what_if_analysis()       NB12 §11, Cell 24 — orchestration over the
                            functions below; no corresponding endpoint
                            contract exists yet in schemas/advisor_request.py.
  full_advisor_report()    NB12 §12, Cell 26 — mixes computation with
                            print()-based reporting; not a pure function.
  get_city_row()           NB12 §2, Cell 5  — superseded by
                            data/data_loader.py's typed accessors.

DEPENDENCIES
────────────
  Standard library : typing (Dict, List, Tuple) — type hints only.
  Internal         : .constants (engineering/financial constants, NB12 §3).
  Explicitly NOT imported: fastapi, pydantic, any backend/services/* module,
  data/data_loader.py. No file I/O is performed anywhere in this module.

A NOTE ON investment_recommendation()
──────────────────────────────────────
  In the source notebook, this function resolves a suitability rank via
  a local SUITABILITY_RANK dict keyed on suitability label strings:
      rank = SUITABILITY_RANK.get(suitability_label, 0)
  Two incompatible versions of that dict exist across the codebase: an
  emoji-keyed version in NB12 §9 Cell 20, and a clean-label version that
  is the single authoritative copy in data/data_loader.py. Importing
  data_loader.py here is disallowed (this module must stay free of
  DataLoader imports), and duplicating either dict would reintroduce the
  exact inconsistency the extraction audit flagged.

  Resolution: this function accepts the already-resolved integer rank
  (`suitability_rank`) instead of the label string. The caller (typically
  AdvisorService) supplies it from SDSFRow.suitability_rank, which is
  computed once, authoritatively, in data/data_loader.py. The decision
  logic itself — the threshold comparisons on rank / payback_years /
  budget_adequate — is otherwise byte-for-byte identical to the notebook.

TESTING INSTRUCTIONS
─────────────────────
  This module has no __main__ smoke test by design (pure functions,
  no side effects to exercise standalone). Validate via
  backend/tests/test_calculations.py (Phase 5), exercising each function
  against the worked examples in NB12 (e.g. the three sample profiles in
  NB12 §4, Cell 10, and their results in §6/§7/§8).
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from .constants import (
    AREA_PER_KW,
    COST_PER_KW,
    DEGRAD_RATE,
    LIFETIME,
    MAX_PHASE1_KW,
    MIN_SYS_KW,
    PERF_RATIO,
    ROOF_UTIL,
    SQ_FT_TO_M2,
    SUBSIDY_3TO10KW,
    SUBSIDY_BELOW_3KW,
    TARIFF,
    TARIFF_ESC,
)

# ─────────────────────────────────────────────────────────────────────────────
# NB12 §5 — Monthly Consumption Estimation (Cell 12)
# ─────────────────────────────────────────────────────────────────────────────

def estimate_consumption(monthly_bill_inr: float, tariff_inr_kwh: float) -> Tuple[float, float]:
    """
    Estimate monthly and annual electricity consumption from a bill amount.

    Formula (unmodified, NB12 §5):
        monthly_kwh = monthly_bill_inr / tariff_inr_kwh
        annual_kwh  = monthly_kwh * 12

    Parameters
    ----------
    monthly_bill_inr : float — Average monthly electricity bill (₹).
    tariff_inr_kwh    : float — Applicable electricity tariff (₹/kWh).

    Returns
    -------
    Tuple[float, float] — (monthly_kwh, annual_kwh).
    """
    monthly_kwh = monthly_bill_inr / tariff_inr_kwh
    annual_kwh = monthly_kwh * 12
    return monthly_kwh, annual_kwh


# ─────────────────────────────────────────────────────────────────────────────
# NB12 §6 — System Size Recommendation Engine (Cell 14)
# ─────────────────────────────────────────────────────────────────────────────

def _snap_to_half_kw(value: float, floor_kw: float) -> float:
    """
    Round to the nearest 0.5 kW (standard commercially available system
    sizes), floored at `floor_kw`.

    Extracted from the nested `snap()` closure inside the notebook's
    recommend_system_sizes() (NB12 §6, Cell 14) and pulled out as a
    private module-level helper per the extraction audit. Formula
    unmodified: max(floor_kw, round(value * 2) / 2).
    """
    return max(floor_kw, round(value * 2) / 2)


def recommend_system_sizes(
    annual_kwh: float,
    roof_sqft: float,
    budget_inr: float,
    mean_ghi: float,
    p10_ghi: float,
    tariff: float = TARIFF,
    cost_kw: float = COST_PER_KW,
    perf: float = PERF_RATIO,
    area_kw: float = AREA_PER_KW,
    roof_util: float = ROOF_UTIL,
    min_kw: float = MIN_SYS_KW,
    max_kw: float = MAX_PHASE1_KW,
) -> Dict[str, float]:
    """
    Compute minimum, recommended, and maximum feasible system sizes (kW),
    rounded to the nearest 0.5 kW.

    Formula (unmodified, NB12 §6):
        roof_m2          = roof_sqft * SQ_FT_TO_M2
        usable_m2        = roof_m2 * roof_util
        min_kw_cons       = (annual_kwh * 0.60) / (p10_ghi  * 365 * perf)
        rec_kw_cons       = (annual_kwh * 0.80) / (mean_ghi * 365 * perf)
        max_kw_roof       = usable_m2 / area_kw
        max_kw_budget     = budget_inr / cost_kw
        max_kw_feasible   = min(max_kw_roof, max_kw_budget, max_kw)
        (then snapped to nearest 0.5 kW, with Min <= Rec <= Max enforced)

    Invariant guaranteed: Min_kW <= Rec_kW <= Max_kW for every output,
    enforced inside the function exactly as in the notebook.

    NOTE: `tariff` is accepted for signature parity with the source
    notebook (NB12 §6, Cell 14), which also declares this parameter but
    never references it in the function body. Preserved as-is — this is
    a notebook artifact, not a defect introduced during extraction.

    Parameters
    ----------
    annual_kwh  : float — Estimated annual electricity consumption (kWh).
    roof_sqft   : float — Total flat roof area available (sq ft).
    budget_inr  : float — Maximum capital available for solar (₹).
    mean_ghi    : float — Mean predicted GHI for the city (kWh/m²/day).
    p10_ghi     : float — 10th-percentile GHI for the city (kWh/m²/day).
    tariff      : float — Unused in this notebook's formula; retained
                  for signature parity. Default: TARIFF.
    cost_kw     : float — Installed system cost (₹/kW). Default: COST_PER_KW.
    perf        : float — Performance ratio. Default: PERF_RATIO.
    area_kw     : float — Roof area required per kW (m²/kW). Default: AREA_PER_KW.
    roof_util   : float — Usable roof fraction. Default: ROOF_UTIL.
    min_kw      : float — Minimum viable system size (kW). Default: MIN_SYS_KW.
    max_kw      : float — Maximum single-phase system size (kW). Default: MAX_PHASE1_KW.

    Returns
    -------
    Dict[str, float] — {"Min_kW", "Rec_kW", "Max_kW", "Roof_m2"}.
    """
    roof_m2 = roof_sqft * SQ_FT_TO_M2
    usable_m2 = roof_m2 * roof_util

    # Consumption-based sizing
    min_kw_cons = (annual_kwh * 0.60) / (p10_ghi * 365 * perf)   # conservative GHI
    rec_kw_cons = (annual_kwh * 0.80) / (mean_ghi * 365 * perf)  # mean GHI

    # Physical / financial / regulatory constraints
    max_kw_roof = usable_m2 / area_kw
    max_kw_budget = budget_inr / cost_kw
    max_kw_feasible = min(max_kw_roof, max_kw_budget, max_kw)

    # Round to nearest 0.5 kW; floor at min_kw
    min_kw_final = _snap_to_half_kw(min_kw_cons, min_kw)
    max_kw_final = _snap_to_half_kw(max_kw_feasible, min_kw)

    # Recommended: consumption-driven but capped by feasibility
    rec_kw_final = _snap_to_half_kw(min(rec_kw_cons, max_kw_feasible), min_kw)

    # Enforce lower bound: Rec >= Min
    if rec_kw_final < min_kw_final:
        rec_kw_final = min_kw_final

    # Enforce upper bound: Rec <= Max
    # (can occur when min_kw_final > max_kw_final on very constrained roofs)
    if rec_kw_final > max_kw_final:
        rec_kw_final = max_kw_final

    return {
        "Min_kW": min_kw_final,
        "Rec_kW": rec_kw_final,
        "Max_kW": max_kw_final,
        "Roof_m2": round(usable_m2, 1),
    }


# ─────────────────────────────────────────────────────────────────────────────
# NB12 §7 — Annual Energy Generation (Cell 16)
# ─────────────────────────────────────────────────────────────────────────────

def annual_generation(system_kw: float, ghi: float, pr: float = PERF_RATIO) -> float:
    """
    Annual generation (kWh) for a system of `system_kw` kW under `ghi`
    irradiance.

    Formula (unmodified, NB12 §7):
        E_annual = system_kw * ghi * 365 * pr

    Parameters
    ----------
    system_kw : float — Installed system capacity (kW).
    ghi       : float — Irradiance to apply (kWh/m²/day) — typically the
                city's Mean / P10 / P50 / P90 GHI value.
    pr        : float — Performance ratio. Default: PERF_RATIO.

    Returns
    -------
    float — Annual generation (kWh).
    """
    return system_kw * ghi * 365 * pr


# ─────────────────────────────────────────────────────────────────────────────
# NB12 §8 — Financial Analysis (Cell 18)
# ─────────────────────────────────────────────────────────────────────────────

def calc_subsidy(
    system_kw: float,
    cost_kw: float = COST_PER_KW,
    sub1: float = SUBSIDY_BELOW_3KW,
    sub2: float = SUBSIDY_3TO10KW,
) -> float:
    """
    PM Surya Ghar Muft Bijli Yojana subsidy (₹).

    Formula (unmodified, NB12 §8):
        tier1   = min(system_kw, 3.0)
        tier2   = max(0.0, min(system_kw, 10.0) - 3.0)
        subsidy = sub1 * cost_kw * tier1 + sub2 * cost_kw * tier2

    NOTE: the 3.0 / 10.0 tier breakpoints are hardcoded literals in the
    source notebook (10.0 corresponds numerically to MAX_PHASE1_KW).
    Preserved exactly as written rather than substituted with the
    constant, per the "preserve formulas exactly" extraction rule.

    Parameters
    ----------
    system_kw : float — Installed system capacity (kW).
    cost_kw   : float — Installed system cost (₹/kW). Default: COST_PER_KW.
    sub1      : float — Subsidy fraction for capacity ≤ 3 kW. Default: SUBSIDY_BELOW_3KW.
    sub2      : float — Subsidy fraction for incremental capacity 3–10 kW. Default: SUBSIDY_3TO10KW.

    Returns
    -------
    float — Subsidy amount (₹).
    """
    tier1 = min(system_kw, 3.0)
    tier2 = max(0.0, min(system_kw, 10.0) - 3.0)
    return sub1 * cost_kw * tier1 + sub2 * cost_kw * tier2


def net_cost(system_kw: float, cost_kw: float = COST_PER_KW) -> float:
    """
    Net installed system cost after government subsidy (₹).

    Formula (unmodified, NB12 §8):
        gross   = system_kw * cost_kw
        net     = gross - calc_subsidy(system_kw, cost_kw)

    Parameters
    ----------
    system_kw : float — Installed system capacity (kW).
    cost_kw   : float — Installed system cost (₹/kW). Default: COST_PER_KW.

    Returns
    -------
    float — Net system cost after subsidy (₹).
    """
    gross = system_kw * cost_kw
    return gross - calc_subsidy(system_kw, cost_kw)


def lifetime_savings_series(
    annual_gen_kwh: float,
    tariff: float,
    years: int = LIFETIME,
    degrad: float = DEGRAD_RATE,
    esc: float = TARIFF_ESC,
) -> List[float]:
    """
    Annual savings (₹) for each year over the system lifetime, accounting
    for panel degradation and tariff escalation.

    Formula (unmodified, NB12 §8):
        S_n = annual_gen_kwh * (1 - degrad)^(n-1) * tariff * (1 + esc)^(n-1)
        for n = 1 .. years

    Parameters
    ----------
    annual_gen_kwh : float — Annual energy generation in Year 1 (kWh).
    tariff         : float — Electricity tariff (₹/kWh).
    years          : int — System lifetime (years). Default: LIFETIME.
    degrad         : float — Annual panel degradation (fraction). Default: DEGRAD_RATE.
    esc            : float — Annual tariff escalation (fraction). Default: TARIFF_ESC.

    Returns
    -------
    List[float] — Annual savings (₹) for each year, length == years.
    """
    return [
        annual_gen_kwh * (1 - degrad) ** (n - 1) * tariff * (1 + esc) ** (n - 1)
        for n in range(1, years + 1)
    ]


def simple_payback(net_cost_inr: float, year1_savings: float) -> float:
    """
    Simple payback period (years).

    Formula (unmodified, NB12 §8):
        payback = net_cost_inr / year1_savings   if year1_savings > 0
        payback = inf                              otherwise

    NOTE: returns float('inf') when year1_savings <= 0, exactly as in
    the notebook. JSON has no native infinity representation; callers at
    the API boundary (e.g. response schemas) are responsible for handling
    that conversion — this module performs no such handling, since it
    must remain free of Pydantic/FastAPI concerns.

    Parameters
    ----------
    net_cost_inr  : float — Net system cost after subsidy (₹).
    year1_savings : float — Year-1 electricity savings (₹).

    Returns
    -------
    float — Payback period in years, or float('inf') if year1_savings <= 0.
    """
    if year1_savings <= 0:
        return float("inf")
    return net_cost_inr / year1_savings


# ─────────────────────────────────────────────────────────────────────────────
# NB12 §9 — Investment Recommendation Engine (Cell 20)
# ─────────────────────────────────────────────────────────────────────────────

def investment_recommendation(
    suitability_rank: int,
    payback_years: float,
    budget_adequate: bool,
) -> Tuple[str, str]:
    """
    Rule-based investment recommendation.

    Decision logic (unmodified, NB12 §9):
        if payback_years > 15 or rank == 0:
            -> ('Not Recommended', 'HIGH_PAYBACK_OR_LOW_SUIT')
        elif rank == 3 and payback_years <= 7 and budget_adequate:
            -> ('Highly Recommended', 'STRONG_RESOURCE_SHORT_PAYBACK')
        elif rank >= 2 and payback_years <= 10:
            -> ('Recommended', 'GOOD_RESOURCE_REASONABLE_PAYBACK')
        elif rank >= 1 and payback_years <= 15:
            -> ('Consider Carefully', 'MODERATE_RESOURCE_OR_LONGER_PAYBACK')
        else:
            -> ('Not Recommended', 'HIGH_PAYBACK_OR_LOW_SUIT')

    NOTE ON `suitability_rank`: the notebook resolves this value via a
    local `SUITABILITY_RANK.get(suitability_label, 0)` lookup. That dict
    is intentionally NOT reproduced in this module — see the module-level
    docstring for why. Callers must pass the pre-resolved integer rank
    (3 = Highly Suitable, 2 = Suitable, 1 = Moderately Suitable,
    0 = Less Suitable / unknown), sourced from the single authoritative
    mapping in data/data_loader.py (e.g. SDSFRow.suitability_rank). The
    threshold comparisons below are otherwise identical to the notebook.

    Parameters
    ----------
    suitability_rank : int — Pre-resolved suitability rank (0-3).
    payback_years    : float — Simple payback period (years).
    budget_adequate  : bool — Whether the homeowner's budget covers the
                       net system cost.

    Returns
    -------
    Tuple[str, str] — (recommendation_str, rationale_code).
    """
    rank = suitability_rank

    if payback_years > 15 or rank == 0:
        return "Not Recommended", "HIGH_PAYBACK_OR_LOW_SUIT"
    elif rank == 3 and payback_years <= 7 and budget_adequate:
        return "Highly Recommended", "STRONG_RESOURCE_SHORT_PAYBACK"
    elif rank >= 2 and payback_years <= 10:
        return "Recommended", "GOOD_RESOURCE_REASONABLE_PAYBACK"
    elif rank >= 1 and payback_years <= 15:
        return "Consider Carefully", "MODERATE_RESOURCE_OR_LONGER_PAYBACK"
    else:
        return "Not Recommended", "HIGH_PAYBACK_OR_LOW_SUIT"
