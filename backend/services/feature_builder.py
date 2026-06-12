"""
feature_builder.py
------------------
Assembles the ordered 31-feature vector expected by the XGBoost model from:

  1. Raw weather data returned by weather_service.fetch_weather()
  2. City name and query date
  3. Climatological lag defaults from city_month_defaults.json

Feature list (from nb08_meta.json, must not be reordered):
  [0]  T2M_MAX
  [1]  TEMP_RANGE
  [2]  RH2M
  [3]  PS
  [4]  WS10M
  [5]  CLOUD_AMT
  [6]  log1p_PREC          = numpy.log1p(PRECTOTCORR)
  [7]  WIND_CLOUD          = WS10M × CLOUD_AMT
  [8]  MONTH_SIN           = sin(2π × month / 12)
  [9]  MONTH_COS           = cos(2π × month / 12)
  [10] IS_MONSOON          = 1 if month in {6,7,8,9} else 0
  [11] DAY_OF_YEAR         = date.timetuple().tm_yday
  [12] GHI_LAG1            = city×month climatological default
  [13] RH2M_LAG1           = city×month climatological default
  [14] CLOUD_LAG1          = city×month climatological default
  [15] GHI_7DAY_MEAN       = city×month climatological default
  [16..30] CITY_<name>     = one-hot, exactly one is 1.0

Lag feature strategy
~~~~~~~~~~~~~~~~~~~~
GHI_LAG1, RH2M_LAG1, CLOUD_LAG1, and GHI_7DAY_MEAN cannot be computed
from a single moment's live weather fetch.  We use city × month
climatological averages from the training data (Option A from the handoff
document).  These are stored in backend/city_month_defaults.json.
This is documented as a limitation; see the project report.
"""

from __future__ import annotations

import json
import logging
import math
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Load lag defaults at module import time
# ---------------------------------------------------------------------------
_DEFAULTS_PATH = Path(__file__).resolve().parent.parent / "city_month_defaults.json"

_lag_defaults: dict[str, dict[str, dict[str, float]]] = {}


def _load_defaults() -> None:
    global _lag_defaults
    with open(_DEFAULTS_PATH, "r", encoding="utf-8") as fh:
        _lag_defaults = json.load(fh)
    logger.info("Loaded lag defaults for %d cities from %s", len(_lag_defaults), _DEFAULTS_PATH)


# Call at import; feature_builder is imported during lifespan startup
_load_defaults()


# ---------------------------------------------------------------------------
# Canonical feature order (mirrors nb08_meta.json)
# ---------------------------------------------------------------------------
FEATURE_LIST = [
    "T2M_MAX", "TEMP_RANGE", "RH2M", "PS", "WS10M", "CLOUD_AMT",
    "log1p_PREC", "WIND_CLOUD",
    "MONTH_SIN", "MONTH_COS", "IS_MONSOON", "DAY_OF_YEAR",
    "GHI_LAG1", "RH2M_LAG1", "CLOUD_LAG1", "GHI_7DAY_MEAN",
    "CITY_Ahmedabad", "CITY_Bengaluru", "CITY_Bhopal", "CITY_Bhubaneswar",
    "CITY_Chandigarh", "CITY_Chennai", "CITY_Delhi", "CITY_Guwahati",
    "CITY_Hyderabad", "CITY_Jaipur", "CITY_Kochi", "CITY_Kolkata",
    "CITY_Mangalore", "CITY_Mumbai", "CITY_Pune",
]

_CITY_COLUMNS = [f for f in FEATURE_LIST if f.startswith("CITY_")]
_MONSOON_MONTHS = {6, 7, 8, 9}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_features(
    city: str,
    query_date: date,
    weather: dict[str, float],
) -> tuple[list[float], dict[str, float]]:
    """Build the 31-feature vector for model inference.

    Parameters
    ----------
    city:
        City name (e.g. ``"Bengaluru"``).
    query_date:
        The date for which GHI is being predicted.
    weather:
        Raw weather dict returned by ``weather_service.fetch_weather()``.
        Expected keys: T2M_MAX, TEMP_RANGE, RH2M, PS, WS10M, CLOUD_AMT,
        PRECTOTCORR.

    Returns
    -------
    (vector, feature_dict)
        ``vector`` — ordered list of 31 floats, ready for predictor.predict()
        ``feature_dict`` — dict mapping feature name → value (for the API response)

    Raises
    ------
    KeyError
        If *city* is not in the defaults lookup.
    ValueError
        If the assembled vector does not have exactly 31 elements.
    """
    month = query_date.month
    lag = _get_lag_defaults(city, month)

    # ── Direct weather features ──────────────────────────────────────────────
    T2M_MAX    = float(weather["T2M_MAX"])
    TEMP_RANGE = float(weather["TEMP_RANGE"])
    RH2M       = float(weather["RH2M"])
    PS         = float(weather["PS"])
    WS10M      = float(weather["WS10M"])
    CLOUD_AMT  = float(weather["CLOUD_AMT"])
    PRECTOTCORR = float(weather["PRECTOTCORR"])

    # ── Engineered features ──────────────────────────────────────────────────
    log1p_PREC  = float(np.log1p(PRECTOTCORR))
    WIND_CLOUD  = round(WS10M * CLOUD_AMT, 4)

    # Cyclic month encoding (month is 1-indexed)
    angle = 2.0 * math.pi * month / 12.0
    MONTH_SIN = round(math.sin(angle), 6)
    MONTH_COS = round(math.cos(angle), 6)

    IS_MONSOON  = 1.0 if month in _MONSOON_MONTHS else 0.0
    DAY_OF_YEAR = float(query_date.timetuple().tm_yday)

    # ── Lag features (climatological defaults) ───────────────────────────────
    GHI_LAG1      = lag["GHI_LAG1"]
    RH2M_LAG1     = lag["RH2M_LAG1"]
    CLOUD_LAG1    = lag["CLOUD_LAG1"]
    GHI_7DAY_MEAN = lag["GHI_7DAY_MEAN"]

    # ── City one-hot ─────────────────────────────────────────────────────────
    city_col = f"CITY_{city}"
    if city_col not in _CITY_COLUMNS:
        raise KeyError(f"City column '{city_col}' not in feature list.")

    city_onehot: dict[str, float] = {col: 0.0 for col in _CITY_COLUMNS}
    city_onehot[city_col] = 1.0

    # ── Assemble dict ────────────────────────────────────────────────────────
    feature_dict: dict[str, float] = {
        "T2M_MAX":      T2M_MAX,
        "TEMP_RANGE":   TEMP_RANGE,
        "RH2M":         RH2M,
        "PS":           PS,
        "WS10M":        WS10M,
        "CLOUD_AMT":    CLOUD_AMT,
        "log1p_PREC":   round(log1p_PREC, 6),
        "WIND_CLOUD":   WIND_CLOUD,
        "MONTH_SIN":    MONTH_SIN,
        "MONTH_COS":    MONTH_COS,
        "IS_MONSOON":   IS_MONSOON,
        "DAY_OF_YEAR":  DAY_OF_YEAR,
        "GHI_LAG1":     GHI_LAG1,
        "RH2M_LAG1":    RH2M_LAG1,
        "CLOUD_LAG1":   CLOUD_LAG1,
        "GHI_7DAY_MEAN": GHI_7DAY_MEAN,
        **city_onehot,
    }

    # ── Build ordered vector ─────────────────────────────────────────────────
    vector = [feature_dict[feat] for feat in FEATURE_LIST]

    # Sanity check
    if len(vector) != 31:
        raise ValueError(
            f"Feature vector length is {len(vector)}, expected 31. "
            "This is a bug in feature_builder.py."
        )

    logger.debug(
        "Built feature vector for city=%s date=%s | "
        "log1p_PREC=%.4f WIND_CLOUD=%.2f IS_MONSOON=%.0f",
        city, query_date, log1p_PREC, WIND_CLOUD, IS_MONSOON,
    )

    return vector, feature_dict


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_lag_defaults(city: str, month: int) -> dict[str, float]:
    """Look up climatological lag defaults for *city* and *month*.

    Raises
    ------
    KeyError
        If *city* is not in the defaults JSON.
    """
    if city not in _lag_defaults:
        raise KeyError(
            f"No lag defaults found for city '{city}'. "
            f"Available: {sorted(_lag_defaults.keys())}"
        )
    city_defaults = _lag_defaults[city]
    month_key = str(month)
    if month_key not in city_defaults:
        raise KeyError(
            f"No lag defaults for city='{city}' month={month}. "
            f"Available months: {sorted(city_defaults.keys())}"
        )
    return city_defaults[month_key]
