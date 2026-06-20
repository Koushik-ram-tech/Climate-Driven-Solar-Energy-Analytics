"""
backend/data/data_loader.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PURPOSE
───────
Single source of truth for all CSV data consumed by the SolarIQ backend.

Responsibilities:
  1. Load both CSVs once at application startup.
  2. Validate schema integrity against the approved architecture mapping.
  3. Normalise column names and field values (strip emoji from Suitability,
     derive city slugs, coerce numeric types).
  4. Expose two typed lookup functions used by every service layer:
       get_sdsf_row(city)     → SDSFRow
       get_advisor_row(city)  → AdvisorRow
  5. Expose a city_list() function used by GET /cities.

What this module does NOT do:
  • Run advisory calculations  (→ AdvisorService, Phase 3)
  • Serve HTTP responses       (→ api/ layer, Phase 4)
  • Load SHAP data             (→ deferred, pending shap_summary.csv)

LOCATION
────────
  backend/data/data_loader.py

DEPENDENCIES
────────────
  Standard library : os, re, logging
  Third-party      : pandas >= 1.5  (already in requirements.txt per architecture doc)
  Internal         : none

  The module is imported by:
    services/readiness_service.py   (get_sdsf_row)
    services/advisor_service.py     (get_sdsf_row, get_advisor_row)
    services/city_service.py        (get_sdsf_row, get_advisor_row, city_list)

  It must be initialised before any service is instantiated.  Call
  DataLoader.load(sdsf_path, advisor_path) once inside the FastAPI
  lifespan handler (main.py), then pass the singleton instance to each
  service via dependency injection.

TESTING INSTRUCTIONS
────────────────────
  Automated tests live in backend/tests/test_data_loader.py (Phase 5).
  For a quick manual smoke-test against the real CSVs, run from the
  backend/ directory:

      python -m data.data_loader

  Expected output (15 rows each, zero errors):

      [data_loader] Loaded 15 SDSF rows from sdsf_city_dashboard.csv
      [data_loader] Loaded 15 Advisor rows from solar_investment_advisor_results.csv
      [data_loader] Schema validation passed.
      [data_loader] All 15 city keys match across both CSVs.
      --- SDSF sample: Bengaluru ---
      SDSFRow(city='Bengaluru', city_slug='bengaluru', mean_ghi=5.272,
              p10_ghi=3.58, p50_ghi=5.37, p90_ghi=6.88,
              reliability_score=81.1, rs_category='Consistent Producer',
              model_rmse=1.5739, model_mape=24.3,
              prediction_confidence='High',
              suitability='Highly Suitable',
              suitability_raw='✅ Highly Suitable',
              explanation='Good solar resource availability...')
      --- Advisor sample: Bengaluru ---
      AdvisorRow(city='Bengaluru', city_slug='bengaluru',
                 system_size_kw=3.0, annual_generation_kwh=4503,
                 annual_savings=31520, payback_years=3.7,
                 lifetime_savings=1224427, net_benefit_inr=1108927,
                 investment_recommendation='Highly Recommended',
                 recommendation_explanation='Bengaluru is Highly Recommended...')
      [data_loader] Smoke test passed.
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from typing import Dict, List

import pandas as pd

from utils.exceptions import DataLoaderError  # noqa: E402 — single authoritative definition

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Expected schema — validated on load
# Source: approved architecture mapping document (Part 1, CSV Schema Analysis)
# ─────────────────────────────────────────────────────────────────────────────

_SDSF_REQUIRED_COLUMNS: List[str] = [
    "City",
    "Mean GHI (kWh/m²/d)",
    "P10 GHI",
    "P50 GHI",
    "P90 GHI",
    "Reliability Score",
    "RS Category",
    "Model RMSE",
    "Model MAPE (%)",
    "Prediction Confidence",
    "Suitability",
    "Explanation",
]

_ADVISOR_REQUIRED_COLUMNS: List[str] = [
    "City",
    "System_Size_kW",
    "Annual_Generation_kWh",
    "Annual_Savings",
    "Payback_Years",
    "Lifetime_Savings",
    "Net_Benefit_INR",
    "Investment_Recommendation",
    "Recommendation_Explanation",
]

# Valid categorical values — sourced directly from the CSVs.
# Any value outside these sets triggers a DataLoaderError on startup.
_VALID_SUITABILITY_RAW: frozenset[str] = frozenset(
    {"✅ Highly Suitable", "👍 Suitable", "⚠️ Moderately Suitable"}
)
_VALID_PREDICTION_CONFIDENCE: frozenset[str] = frozenset({"High", "Medium", "Low"})
_VALID_RS_CATEGORY: frozenset[str] = frozenset(
    {"Consistent Producer", "Seasonal Producer", "Monsoon Sensitive", "Highly Variable"}
)
_VALID_INVESTMENT_RECOMMENDATION: frozenset[str] = frozenset(
    {"Highly Recommended", "Recommended", "Consider Carefully", "Not Recommended"}
)

# Emoji-prefix → clean label mapping.
# The raw Suitability value in the CSV includes the emoji (e.g. "✅ Highly Suitable").
# The emoji is stripped here so downstream services and the recommendation engine
# operate on a clean string.  The raw value is preserved in suitability_raw.
_SUITABILITY_CLEAN: Dict[str, str] = {
    "✅ Highly Suitable": "Highly Suitable",
    "👍 Suitable": "Suitable",
    "⚠️ Moderately Suitable": "Moderately Suitable",
}

# Suitability rank — used by AdvisorService recommendation engine (NB12 §9).
# Stored here as the single authoritative definition to avoid duplication.
SUITABILITY_RANK: Dict[str, int] = {
    "Highly Suitable": 3,
    "Suitable": 2,
    "Moderately Suitable": 1,
    "Less Suitable": 0,
}

# ─────────────────────────────────────────────────────────────────────────────
# Typed row dataclasses
# Services receive these, never raw DataFrames.  This decouples the service
# layer from pandas and makes IDE type-checking and unit testing straightforward.
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class SDSFRow:
    """
    One row from sdsf_city_dashboard.csv, fully normalised.

    Sourced from Notebook 11 (Solar Decision Support Framework).
    All values are frozen research outputs — never recomputed by the backend.
    """
    city: str
    city_slug: str

    # Irradiance
    mean_ghi: float          # Annual mean predicted GHI (kWh/m²/d)
    p10_ghi: float           # 10th-percentile GHI — conservative sizing input
    p50_ghi: float           # Median GHI — base-case scenario
    p90_ghi: float           # 90th-percentile GHI — optimistic scenario

    # Reliability
    reliability_score: float # 0–100 composite score (MDI + SCV + GDF)
    rs_category: str         # "Consistent Producer" | "Seasonal Producer" | ...

    # Model accuracy
    model_rmse: float        # City-level XGBoost RMSE
    model_mape: float        # City-level MAPE (%)

    # Confidence & suitability
    prediction_confidence: str  # "High" | "Medium" | "Low"
    suitability: str            # Clean label: "Highly Suitable" | "Suitable" | "Moderately Suitable"
    suitability_raw: str        # Original value with emoji prefix
    suitability_rank: int       # Numeric rank 3/2/1/0 for recommendation engine

    # Explanation
    explanation: str         # Plain-language suitability rationale from NB11


@dataclass(frozen=True)
class AdvisorRow:
    """
    One row from solar_investment_advisor_results.csv, fully normalised.

    Sourced from Notebook 12 (Residential Solar Investment Advisor).
    These values represent the default user profile outputs.
    City Explorer cards and quick-view modals use these directly.
    POST /advisor for personalised inputs does NOT use these values —
    AdvisorService recomputes using NB12 formulas.
    """
    city: str
    city_slug: str

    # System
    system_size_kw: float           # Recommended system size (kW), snapped to 0.5 kW
    annual_generation_kwh: int      # Annual energy output (kWh)

    # Financials
    annual_savings: int             # Year-1 electricity savings (₹)
    payback_years: float            # Net-cost / Year-1-savings
    lifetime_savings: int           # 25-year cumulative savings (₹)
    net_benefit_inr: int            # lifetime_savings − net_system_cost (₹)

    # Recommendation
    investment_recommendation: str  # "Highly Recommended" | "Recommended" | "Consider Carefully"
    recommendation_explanation: str # Template-rendered narrative from NB12 §10


# ─────────────────────────────────────────────────────────────────────────────
# Exception
# DataLoaderError is imported from utils.exceptions — single definition.
# All raise sites in this module use the imported class unchanged.
# ─────────────────────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_slug(city_name: str) -> str:
    """
    Derive a URL-safe slug from a city name.

    Examples
    --------
    "Bengaluru"   → "bengaluru"
    "Bhubaneswar" → "bhubaneswar"

    The slug is used in /results/[city-slug] frontend routes and in
    GET /cities responses so the frontend can build links without
    string-manipulation logic.
    """
    return re.sub(r"[^a-z0-9]+", "-", city_name.lower()).strip("-")


def _validate_columns(df: pd.DataFrame, required: List[str], source: str) -> None:
    """Raise DataLoaderError if any required column is missing."""
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise DataLoaderError(
            f"[data_loader] {source} is missing required columns: {missing}\n"
            f"Found columns: {df.columns.tolist()}"
        )


def _validate_categoricals(df: pd.DataFrame, source: str) -> None:
    """
    Check that all categorical fields contain only known values.
    Unknown values indicate a data pipeline change that must be reviewed.
    """
    if source == "SDSF":
        bad_suit = set(df["Suitability"]) - _VALID_SUITABILITY_RAW
        if bad_suit:
            raise DataLoaderError(
                f"[data_loader] Unknown Suitability values in SDSF CSV: {bad_suit}\n"
                f"Expected one of: {_VALID_SUITABILITY_RAW}"
            )
        bad_conf = set(df["Prediction Confidence"]) - _VALID_PREDICTION_CONFIDENCE
        if bad_conf:
            raise DataLoaderError(
                f"[data_loader] Unknown Prediction Confidence values: {bad_conf}"
            )
        bad_rs = set(df["RS Category"]) - _VALID_RS_CATEGORY
        if bad_rs:
            raise DataLoaderError(
                f"[data_loader] Unknown RS Category values: {bad_rs}"
            )

    if source == "Advisor":
        bad_rec = set(df["Investment_Recommendation"]) - _VALID_INVESTMENT_RECOMMENDATION
        if bad_rec:
            raise DataLoaderError(
                f"[data_loader] Unknown Investment_Recommendation values: {bad_rec}"
            )


def _validate_city_alignment(sdsf_df: pd.DataFrame, advisor_df: pd.DataFrame) -> None:
    """
    Both CSVs must contain exactly the same 15 city names.
    A mismatch means the files are from different pipeline runs.
    """
    sdsf_cities = set(sdsf_df["City"])
    advisor_cities = set(advisor_df["City"])
    only_in_sdsf = sdsf_cities - advisor_cities
    only_in_advisor = advisor_cities - sdsf_cities
    if only_in_sdsf or only_in_advisor:
        raise DataLoaderError(
            f"[data_loader] City mismatch between CSVs.\n"
            f"  In SDSF only    : {sorted(only_in_sdsf)}\n"
            f"  In Advisor only : {sorted(only_in_advisor)}"
        )


def _validate_no_nulls(df: pd.DataFrame, source: str) -> None:
    """All columns must be fully populated — nulls indicate a broken export."""
    null_counts = df.isnull().sum()
    bad = null_counts[null_counts > 0]
    if not bad.empty:
        raise DataLoaderError(
            f"[data_loader] Null values found in {source} CSV:\n{bad.to_string()}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# DataLoader
# ─────────────────────────────────────────────────────────────────────────────

class DataLoader:
    """
    Loads, validates, and indexes both CSVs at application startup.

    Usage (in main.py lifespan handler)
    ------------------------------------
        loader = DataLoader()
        loader.load(
            sdsf_path   = "data/sdsf_city_dashboard.csv",
            advisor_path = "data/solar_investment_advisor_results.csv",
        )
        # Pass loader to services via dependency injection.

    After load() returns, the following attributes are populated:

        loader.sdsf_index    : Dict[str, SDSFRow]   — keyed by exact city name
        loader.advisor_index : Dict[str, AdvisorRow] — keyed by exact city name
        loader.slug_to_city  : Dict[str, str]        — URL slug → exact city name
        loader.cities        : List[str]             — sorted list of city names

    Thread safety
    -------------
    The loader is read-only after load() completes.  Concurrent reads are safe.
    There is no write path after startup.
    """

    def __init__(self) -> None:
        self._loaded: bool = False
        self.sdsf_index: Dict[str, SDSFRow] = {}
        self.advisor_index: Dict[str, AdvisorRow] = {}
        self.slug_to_city: Dict[str, str] = {}
        self.cities: List[str] = []

    # ── Public interface ──────────────────────────────────────────────────────

    def load(self, sdsf_path: str, advisor_path: str) -> None:
        """
        Load and validate both CSVs.  Must be called exactly once at startup.
        Raises DataLoaderError on any validation failure — the application
        must not start with invalid data.

        Parameters
        ----------
        sdsf_path    : Path to sdsf_city_dashboard.csv
        advisor_path : Path to solar_investment_advisor_results.csv
        """
        if self._loaded:
            logger.warning("[data_loader] load() called more than once — ignoring.")
            return

        logger.info("[data_loader] Loading CSV files...")

        sdsf_df   = self._read_csv(sdsf_path,   "sdsf_city_dashboard.csv")
        advisor_df = self._read_csv(advisor_path, "solar_investment_advisor_results.csv")

        # Schema validation
        _validate_columns(sdsf_df,    _SDSF_REQUIRED_COLUMNS,   "SDSF CSV")
        _validate_columns(advisor_df, _ADVISOR_REQUIRED_COLUMNS, "Advisor CSV")
        _validate_no_nulls(sdsf_df,    "SDSF")
        _validate_no_nulls(advisor_df, "Advisor")
        _validate_categoricals(sdsf_df,    "SDSF")
        _validate_categoricals(advisor_df, "Advisor")
        _validate_city_alignment(sdsf_df, advisor_df)

        logger.info(
            "[data_loader] Schema validation passed. "
            f"Loaded {len(sdsf_df)} SDSF rows, {len(advisor_df)} Advisor rows."
        )

        # Build in-memory indexes
        self._build_sdsf_index(sdsf_df)
        self._build_advisor_index(advisor_df)
        self._build_slug_index()

        self.cities = sorted(self.sdsf_index.keys())
        self._loaded = True

        logger.info(
            f"[data_loader] Ready. {len(self.cities)} cities indexed: "
            f"{self.cities}"
        )

    def get_sdsf_row(self, city: str) -> SDSFRow:
        """
        Return the SDSFRow for a city.

        Parameters
        ----------
        city : Exact city name as it appears in the CSV (e.g. "Bengaluru").
               Case-sensitive.  Use resolve_city() first if the input comes
               from a URL slug.

        Raises
        ------
        DataLoaderError : If load() has not been called.
        KeyError        : If the city is not in the supported list.
                          Callers (service layer) catch this and raise HTTP 404.
        """
        self._assert_loaded()
        return self.sdsf_index[city]

    def get_advisor_row(self, city: str) -> AdvisorRow:
        """
        Return the AdvisorRow for a city (default-profile outputs).

        Used by CityService for City Explorer cards.
        NOT used by AdvisorService for personalised calculations —
        AdvisorService reads SDSF GHI values and computes fresh outputs.

        Raises
        ------
        DataLoaderError : If load() has not been called.
        KeyError        : If the city is not in the supported list.
        """
        self._assert_loaded()
        return self.advisor_index[city]

    def resolve_city(self, slug_or_name: str) -> str:
        """
        Resolve a URL slug or exact city name to the canonical city name
        as it appears in the CSV.

        Examples
        --------
        "bengaluru"   → "Bengaluru"
        "Bengaluru"   → "Bengaluru"   (direct match, no slug lookup needed)
        "bhubaneswar" → "Bhubaneswar"

        Returns
        -------
        Canonical city name string.

        Raises
        ------
        KeyError : If neither the slug nor the name is recognised.
                   Callers translate this to HTTP 404.
        """
        self._assert_loaded()

        # Try exact name match first (POST /advisor sends the name directly)
        if slug_or_name in self.sdsf_index:
            return slug_or_name

        # Try slug lookup (GET /readiness/{city} uses the slug from the URL)
        if slug_or_name in self.slug_to_city:
            return self.slug_to_city[slug_or_name]

        raise KeyError(
            f"City not recognised: {repr(slug_or_name)}. "
            f"Supported cities: {self.cities}"
        )

    def city_list(self) -> List[str]:
        """Return the sorted list of all supported city names."""
        self._assert_loaded()
        return self.cities

    # ── Private helpers ───────────────────────────────────────────────────────

    def _assert_loaded(self) -> None:
        if not self._loaded:
            raise DataLoaderError(
                "[data_loader] DataLoader.load() has not been called. "
                "Ensure it is initialised in the FastAPI lifespan handler before "
                "any service is used."
            )

    @staticmethod
    def _read_csv(path: str, label: str) -> pd.DataFrame:
        """Read a CSV, raising DataLoaderError with a clear message on failure."""
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            raise DataLoaderError(
                f"[data_loader] {label} not found at: {abs_path}\n"
                f"Ensure the file exists at backend/data/{label}"
            )
        try:
            df = pd.read_csv(abs_path, encoding="utf-8")
        except Exception as exc:
            raise DataLoaderError(
                f"[data_loader] Failed to read {label}: {exc}"
            ) from exc

        logger.info(f"[data_loader] Read {len(df)} rows from {label}")
        return df

    def _build_sdsf_index(self, df: pd.DataFrame) -> None:
        """Parse SDSF DataFrame into SDSFRow objects, keyed by city name."""
        for _, row in df.iterrows():
            city          = str(row["City"])
            suitability_raw = str(row["Suitability"])
            suitability_clean = _SUITABILITY_CLEAN.get(
                suitability_raw, suitability_raw  # fallback: use raw if mapping missing
            )
            self.sdsf_index[city] = SDSFRow(
                city                 = city,
                city_slug            = _make_slug(city),
                mean_ghi             = float(row["Mean GHI (kWh/m²/d)"]),
                p10_ghi              = float(row["P10 GHI"]),
                p50_ghi              = float(row["P50 GHI"]),
                p90_ghi              = float(row["P90 GHI"]),
                reliability_score    = float(row["Reliability Score"]),
                rs_category          = str(row["RS Category"]),
                model_rmse           = float(row["Model RMSE"]),
                model_mape           = float(row["Model MAPE (%)"]),
                prediction_confidence = str(row["Prediction Confidence"]),
                suitability          = suitability_clean,
                suitability_raw      = suitability_raw,
                suitability_rank     = SUITABILITY_RANK.get(suitability_clean, 0),
                explanation          = str(row["Explanation"]),
            )

    def _build_advisor_index(self, df: pd.DataFrame) -> None:
        """Parse Advisor DataFrame into AdvisorRow objects, keyed by city name."""
        for _, row in df.iterrows():
            city = str(row["City"])
            self.advisor_index[city] = AdvisorRow(
                city                       = city,
                city_slug                  = _make_slug(city),
                system_size_kw             = float(row["System_Size_kW"]),
                annual_generation_kwh      = int(row["Annual_Generation_kWh"]),
                annual_savings             = int(row["Annual_Savings"]),
                payback_years              = float(row["Payback_Years"]),
                lifetime_savings           = int(row["Lifetime_Savings"]),
                net_benefit_inr            = int(row["Net_Benefit_INR"]),
                investment_recommendation  = str(row["Investment_Recommendation"]),
                recommendation_explanation = str(row["Recommendation_Explanation"]),
            )

    def _build_slug_index(self) -> None:
        """Build slug → city_name reverse lookup from the SDSF index."""
        for city, sdsf_row in self.sdsf_index.items():
            self.slug_to_city[sdsf_row.city_slug] = city


# ─────────────────────────────────────────────────────────────────────────────
# Module-level singleton
# ─────────────────────────────────────────────────────────────────────────────

# Instantiated here; load() is called in main.py.
# Services import this object directly:
#
#     from data.data_loader import loader
#
# This avoids re-instantiation across imports and keeps the startup call
# in one place (main.py lifespan).

loader = DataLoader()


# ─────────────────────────────────────────────────────────────────────────────
# Smoke test (python -m data.data_loader)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    # Resolve paths relative to this file's location (backend/data/)
    _here = os.path.dirname(os.path.abspath(__file__))
    _sdsf_path   = os.path.join(_here, "sdsf_city_dashboard.csv")
    _advisor_path = os.path.join(_here, "solar_investment_advisor_results.csv")

    try:
        loader.load(_sdsf_path, _advisor_path)
    except DataLoaderError as e:
        print(f"\n❌ DataLoaderError:\n{e}", file=sys.stderr)
        sys.exit(1)

    # --- SDSF sample ---
    sample_city = "Bengaluru"
    sdsf_row = loader.get_sdsf_row(sample_city)
    print(f"\n--- SDSF sample: {sample_city} ---")
    print(f"  city_slug           : {sdsf_row.city_slug}")
    print(f"  mean_ghi            : {sdsf_row.mean_ghi}")
    print(f"  p10/p50/p90         : {sdsf_row.p10_ghi} / {sdsf_row.p50_ghi} / {sdsf_row.p90_ghi}")
    print(f"  reliability_score   : {sdsf_row.reliability_score}")
    print(f"  rs_category         : {sdsf_row.rs_category}")
    print(f"  model_rmse          : {sdsf_row.model_rmse}")
    print(f"  model_mape          : {sdsf_row.model_mape}")
    print(f"  prediction_confidence: {sdsf_row.prediction_confidence}")
    print(f"  suitability         : {sdsf_row.suitability!r}  (clean)")
    print(f"  suitability_raw     : {sdsf_row.suitability_raw!r}")
    print(f"  suitability_rank    : {sdsf_row.suitability_rank}")
    print(f"  explanation         : {sdsf_row.explanation[:60]}...")

    # --- Advisor sample ---
    adv_row = loader.get_advisor_row(sample_city)
    print(f"\n--- Advisor sample: {sample_city} ---")
    print(f"  city_slug                  : {adv_row.city_slug}")
    print(f"  system_size_kw             : {adv_row.system_size_kw}")
    print(f"  annual_generation_kwh      : {adv_row.annual_generation_kwh}")
    print(f"  annual_savings             : ₹{adv_row.annual_savings:,}")
    print(f"  payback_years              : {adv_row.payback_years}")
    print(f"  lifetime_savings           : ₹{adv_row.lifetime_savings:,}")
    print(f"  net_benefit_inr            : ₹{adv_row.net_benefit_inr:,}")
    print(f"  investment_recommendation  : {adv_row.investment_recommendation!r}")
    print(f"  recommendation_explanation : {adv_row.recommendation_explanation[:60]}...")

    # --- Slug resolution ---
    print("\n--- Slug resolution ---")
    for slug, name in sorted(loader.slug_to_city.items()):
        resolved = loader.resolve_city(slug)
        assert resolved == name, f"Slug resolution failed: {slug} → {resolved} (expected {name})"
        print(f"  {slug:<15} → {resolved}")

    # --- City list ---
    print(f"\n--- City list ({len(loader.cities)} cities) ---")
    print(f"  {loader.cities}")

    # --- All cities load cleanly ---
    print("\n--- Full index validation ---")
    errors = []
    for city in loader.cities:
        try:
            s = loader.get_sdsf_row(city)
            a = loader.get_advisor_row(city)
            assert s.city == a.city == city
            assert s.city_slug == a.city_slug
            assert 0 < s.mean_ghi < 10
            assert 0 < s.reliability_score <= 100
            assert s.suitability_rank in (0, 1, 2, 3)
            assert a.payback_years > 0
            assert a.annual_savings > 0
        except Exception as exc:
            errors.append(f"  {city}: {exc}")

    if errors:
        print("❌ Validation errors:")
        for e in errors:
            print(e)
        sys.exit(1)
    else:
        print(f"  ✅ All {len(loader.cities)} cities passed assertion checks.")

    print("\n✅ Smoke test passed.")
