"""
weather_service.py
------------------
Fetches daily weather data for a given city and date from the Open-Meteo
Historical Weather API (https://archive-api.open-meteo.com).

Open-Meteo is free, requires no API key, and covers all 15 supported Indian
cities.  Historical data is available from 1940-01-01.

Variable mapping
~~~~~~~~~~~~~~~~
NASA POWER variable  ←→  Open-Meteo variable
──────────────────────────────────────────────
T2M_MAX              ←  temperature_2m_max         (°C)
T2M_MIN              ←  temperature_2m_min          (°C)   → used to compute TEMP_RANGE
RH2M                 ←  (computed from dewpoint)    (%)
PS                   ←  surface_pressure            (hPa → kPa ÷ 10)
WS10M                ←  wind_speed_10m_max          (km/h → m/s ÷ 3.6)
CLOUD_AMT            ←  cloud_cover_mean            (%)
PRECTOTCORR          ←  precipitation_sum           (mm)

Note: Open-Meteo does not directly expose RH2M.  We derive it from
dewpoint_2m_mean using the Magnus formula, which is standard practice.

References:
  https://open-meteo.com/en/docs/historical-weather-api
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Open-Meteo endpoint
# ---------------------------------------------------------------------------
_BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

_DAILY_VARS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "dewpoint_2m_mean",
    "surface_pressure_mean",
    "wind_speed_10m_max",
    "cloud_cover_mean",
    "precipitation_sum",
]

# ---------------------------------------------------------------------------
# Humidity helpers
# ---------------------------------------------------------------------------

def _dewpoint_to_rh(t_celsius: float, td_celsius: float) -> float:
    """Approximate relative humidity from temperature and dewpoint (Magnus formula).

    Returns RH in percent [0, 100].
    """
    # Magnus constants (Alduchov & Eskridge 1996)
    a, b = 17.625, 243.04
    rh = 100.0 * (
        (a * td_celsius / (b + td_celsius))
        - (a * t_celsius / (b + t_celsius))
    )
    # exp form: rh = 100 * exp(a*td/(b+td)) / exp(a*t/(b+t))
    import math
    rh = 100.0 * math.exp(a * td_celsius / (b + td_celsius)) / math.exp(a * t_celsius / (b + t_celsius))
    return max(0.0, min(100.0, round(rh, 1)))


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

def _latest_available_date() -> date:
    """Return the latest date safely requestable from Open-Meteo's archive.

    The archive typically lags the real-world clock by one to two days.
    Using yesterday as the upper bound guarantees we never request a date
    that is ahead of the archive, regardless of the server's local time.
    """
    return date.today() - timedelta(days=1)


def _clamp_to_available(target_date: date) -> date:
    """Clamp *target_date* so it never exceeds the latest available archive date.

    If the caller passes today or a future date the archive returns HTTP 400.
    We silently fall back to yesterday, which is always available.
    """
    ceiling = _latest_available_date()
    if target_date > ceiling:
        logger.warning(
            "Requested date %s is ahead of Open-Meteo archive ceiling %s; "
            "falling back to %s.",
            target_date, ceiling, ceiling,
        )
        return ceiling
    return target_date


# ---------------------------------------------------------------------------
# Main fetch function
# ---------------------------------------------------------------------------

async def fetch_weather(city: str, target_date: date) -> dict[str, float]:
    """Fetch daily weather for *city* on *target_date* from Open-Meteo.

    Parameters
    ----------
    city:
        City name (must be present in ``CITY_COORDS``).
    target_date:
        The date for which weather is requested.  If this date is today or
        in the future (i.e. beyond the Open-Meteo archive ceiling) it is
        automatically clamped to yesterday so the request never fails with
        an out-of-range HTTP 400 error.

    Returns
    -------
    dict with keys matching NASA POWER variable names:
        ``T2M_MAX``, ``TEMP_RANGE``, ``RH2M``, ``PS``, ``WS10M``,
        ``CLOUD_AMT``, ``PRECTOTCORR``

    Raises
    ------
    httpx.HTTPStatusError
        If Open-Meteo returns a non-2xx status.
    ValueError
        If the response is missing expected variables.
    """
    from services.city_coords import get_coords

    # Clamp target_date to the latest date available in the archive.
    # Open-Meteo lags real-time by ~1-2 days; yesterday is always safe.
    safe_date = _clamp_to_available(target_date)

    coords = get_coords(city)
    date_str = safe_date.strftime("%Y-%m-%d")

    params = {
        "latitude":         coords["lat"],
        "longitude":        coords["lon"],
        "start_date":       date_str,
        "end_date":         date_str,
        "daily":            ",".join(_DAILY_VARS),
        "timezone":         "Asia/Kolkata",
    }

    logger.info("Fetching Open-Meteo weather: city=%s date=%s", city, date_str)

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(_BASE_URL, params=params)
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()

    daily = data.get("daily", {})
    _require_keys(daily, _DAILY_VARS, city, date_str)

    # Each variable is a list with one entry (we queried a single day)
    idx = 0

    t_max = _get_val(daily, "temperature_2m_max", idx)
    t_min = _get_val(daily, "temperature_2m_min", idx)
    td    = _get_val(daily, "dewpoint_2m_mean", idx)
    ps_hpa = _get_val(daily, "surface_pressure_mean", idx)
    ws_kmh = _get_val(daily, "wind_speed_10m_max", idx)
    cloud  = _get_val(daily, "cloud_cover_mean", idx)
    prec   = _get_val(daily, "precipitation_sum", idx, default=0.0)

    # --- Unit conversions ---
    # TEMP_RANGE = T2M_MAX − T2M_MIN
    temp_range = round(t_max - t_min, 2)

    # RH2M — derive from mean temperature + dewpoint
    t_mean = (t_max + t_min) / 2.0
    rh = _dewpoint_to_rh(t_mean, td)

    # PS: hPa → kPa
    ps_kpa = round(ps_hpa / 10.0, 2)

    # WS10M: km/h → m/s
    ws_ms = round(ws_kmh / 3.6, 2)

    # Guard against null / NaN values from API
    cloud = float(cloud) if cloud is not None else 0.0
    prec  = float(prec)  if prec  is not None else 0.0

    result = {
        "T2M_MAX":     round(float(t_max), 2),
        "TEMP_RANGE":  temp_range,
        "RH2M":        rh,
        "PS":          ps_kpa,
        "WS10M":       ws_ms,
        "CLOUD_AMT":   round(cloud, 1),
        "PRECTOTCORR": round(prec, 2),
    }

    logger.info("Weather fetched: %s", result)
    return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _require_keys(daily: dict, keys: list[str], city: str, date_str: str) -> None:
    for k in keys:
        if k not in daily:
            raise ValueError(
                f"Open-Meteo response missing '{k}' for city={city} date={date_str}. "
                f"Available keys: {list(daily.keys())}"
            )


def _get_val(daily: dict, key: str, idx: int, default: float | None = None) -> float:
    vals = daily.get(key, [])
    if not vals or idx >= len(vals) or vals[idx] is None:
        if default is not None:
            return default
        raise ValueError(f"Open-Meteo returned null for '{key}'[{idx}].")
    return float(vals[idx])
