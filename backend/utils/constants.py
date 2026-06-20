"""
backend/utils/constants.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PURPOSE
───────
Single source of truth for the engineering and financial constants used
by the live recomputation path (AdvisorService / POST /advisor).

SOURCE NOTEBOOK
───────────────
  Notebook 12 — Residential Solar Investment Advisor
  Section 3 "Engineering Assumptions" (Cell 8)

  Every value below is copied verbatim from that cell. No value has been
  invented, rounded, or otherwise modified. The formulas that consume
  these constants live in backend/utils/calculations.py and are likewise
  unmodified from the notebook.

SCOPE NOTE
──────────
  Notebook 11 (Solar Decision Support Framework) outputs are frozen
  research results served as-is from sdsf_city_dashboard.csv — they are
  never recomputed by the backend (see schemas/readiness_response.py).
  Accordingly, NB11-only thresholds (e.g. GHI_THRESHOLD, reliability
  score weights, suitability GHI brackets) are intentionally NOT included
  in this module.

  SUITABILITY_RANK is also intentionally NOT duplicated here. It is
  defined once, authoritatively, in data/data_loader.py, keyed on the
  *clean* suitability label ("Highly Suitable", not "✅ Highly Suitable").
  Import it from there — do not redefine it against the emoji-keyed
  version found in NB12 §9, Cell 20.

DEPENDENCIES
────────────
  None. Pure constants module — no imports required.

USAGE
─────
  from utils.constants import (
      PERF_RATIO, AREA_PER_KW, ROOF_UTIL, COST_PER_KW, TARIFF,
      LIFETIME, DEGRAD_RATE, TARIFF_ESC, SUBSIDY_BELOW_3KW,
      SUBSIDY_3TO10KW, MIN_SYS_KW, MAX_PHASE1_KW, SQ_FT_TO_M2,
  )
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# PV System Technical Parameters
# Source: NB12 §3, Cell 8
# ─────────────────────────────────────────────────────────────────────────────

PANEL_EFF: float = 0.20
# Panel efficiency (fraction). Standard monocrystalline Si
# (2024 market median: 19-22%). Used to derive AREA_PER_KW; not
# referenced directly in the generation formula, which uses PERF_RATIO
# to account for all system losses.
# [NB12 §3, Cell 8 — "PANEL_EFF        = 0.20"]

PERF_RATIO: float = 0.78
# Performance ratio (fraction). Accounts for inverter losses, wiring,
# soiling, mismatch (MNRE standard: 0.75-0.80).
# [NB12 §3, Cell 8 — "PERF_RATIO       = 0.78"]

AREA_PER_KW: float = 6.5
# Roof area required per kW installed (m²/kW). Based on standard 330 Wp
# panels (~1.7 m²/panel), 3.03 panels/kW = 5.15 m²/kW panel area, plus
# ~26% for inter-row spacing and mounting clearance (MNRE installation
# guidelines).
# [NB12 §3, Cell 8 — "AREA_PER_KW      = 6.5"]

ROOF_UTIL: float = 0.70
# Minimum usable roof fraction. Accounts for shading, setbacks, water
# tank exclusion zones.
# [NB12 §3, Cell 8 — "ROOF_UTIL        = 0.70"]

# ─────────────────────────────────────────────────────────────────────────────
# Financial Parameters
# Source: NB12 §3, Cell 8
# ─────────────────────────────────────────────────────────────────────────────

COST_PER_KW: int = 55_000
# Installed system cost (₹/kW), incl. panels, inverter, mounting, wiring
# (2024 Indian market: ₹50k-₹65k/kW).
# [NB12 §3, Cell 8 — "COST_PER_KW      = 55_000"]

TARIFF: float = 7.0
# Baseline electricity tariff (₹/kWh). Residential tier-2 average across
# Tier-1 Indian cities (range: ₹5-₹10/kWh). Fixed system constant per the
# approved architecture decision — not a user input (see
# schemas/advisor_request.py).
# [NB12 §3, Cell 8 — "TARIFF           = 7.0"]

LIFETIME: int = 25
# System lifetime (years). Industry standard; panel warranty typically
# 25 years.
# [NB12 §3, Cell 8 — "LIFETIME         = 25"]

DEGRAD_RATE: float = 0.005
# Annual panel degradation (fraction/year). 0.5%/year - manufacturer
# guarantee floor (NREL data: 0.36-0.8%/year).
# [NB12 §3, Cell 8 — "DEGRAD_RATE      = 0.005"]

TARIFF_ESC: float = 0.04
# Annual tariff escalation (fraction/year). 4%/year - consistent with
# CERC historical averages (2015-2024).
# [NB12 §3, Cell 8 — "TARIFF_ESC       = 0.04"]

# ─────────────────────────────────────────────────────────────────────────────
# Government Subsidy — PM Surya Ghar Muft Bijli Yojana (2024)
# Source: NB12 §3, Cell 8
# ─────────────────────────────────────────────────────────────────────────────

SUBSIDY_BELOW_3KW: float = 0.30
# Subsidy fraction on system capacity up to 3 kW.
# PM Surya Ghar Muft Bijli Yojana (2024): 30% of system cost.
# [NB12 §3, Cell 8 — "SUBSIDY_BELOW_3KW  = 0.30"]

SUBSIDY_3TO10KW: float = 0.15
# Subsidy fraction on incremental capacity between 3 kW and 10 kW.
# PM Surya Ghar: 15% of incremental cost above 3 kW.
# [NB12 §3, Cell 8 — "SUBSIDY_3TO10KW    = 0.15"]

# ─────────────────────────────────────────────────────────────────────────────
# System Size Constraints
# Source: NB12 §3, Cell 8
# ─────────────────────────────────────────────────────────────────────────────

MIN_SYS_KW: float = 1.0
# Minimum viable system size (kW). Below 1 kW, payback economics become
# unfavourable.
# [NB12 §3, Cell 8 — "MIN_SYS_KW       = 1.0"]

MAX_PHASE1_KW: float = 10.0
# Maximum single-phase system size (kW). DISCOM limit for single-phase
# net metering in India. Also the upper subsidy-tier boundary consumed
# by calc_subsidy() in calculations.py.
# [NB12 §3, Cell 8 — "MAX_PHASE1_KW    = 10.0"]

# ─────────────────────────────────────────────────────────────────────────────
# Derived Constant
# Source: NB12 §3, Cell 8 (labelled "Derived constant" in the notebook)
# ─────────────────────────────────────────────────────────────────────────────

SQ_FT_TO_M2: float = 0.0929
# Unit conversion: 1 sq ft = 0.0929 m². Used to convert roof_area_sqft
# (user input, per schemas/advisor_request.py) into m² inside
# recommend_system_sizes().
# [NB12 §3, Cell 8 — "SQ_FT_TO_M2      = 0.0929"]
