"""
city_coords.py
--------------
Latitude / longitude for each of the 15 supported cities.

Used by weather_service.py to call the Open-Meteo API.
Coordinates are city-centre approximations; sub-km precision is unnecessary
for daily climate API calls.
"""

from __future__ import annotations

# { city_name: {"lat": float, "lon": float} }
CITY_COORDS: dict[str, dict[str, float]] = {
    "Ahmedabad":   {"lat": 23.0225, "lon": 72.5714},
    "Bengaluru":   {"lat": 12.9716, "lon": 77.5946},
    "Bhopal":      {"lat": 23.2599, "lon": 77.4126},
    "Bhubaneswar": {"lat": 20.2961, "lon": 85.8245},
    "Chandigarh":  {"lat": 30.7333, "lon": 76.7794},
    "Chennai":     {"lat": 13.0827, "lon": 80.2707},
    "Delhi":       {"lat": 28.6139, "lon": 77.2090},
    "Guwahati":    {"lat": 26.1445, "lon": 91.7362},
    "Hyderabad":   {"lat": 17.3850, "lon": 78.4867},
    "Jaipur":      {"lat": 26.9124, "lon": 75.7873},
    "Kochi":       {"lat": 9.9312,  "lon": 76.2673},
    "Kolkata":     {"lat": 22.5726, "lon": 88.3639},
    "Mangalore":   {"lat": 12.8698, "lon": 74.8428},
    "Mumbai":      {"lat": 19.0760, "lon": 72.8777},
    "Pune":        {"lat": 18.5204, "lon": 73.8567},
}


def get_coords(city: str) -> dict[str, float]:
    """Return {"lat": ..., "lon": ...} for the given city.

    Raises
    ------
    KeyError
        If *city* is not in the supported set.
    """
    if city not in CITY_COORDS:
        supported = sorted(CITY_COORDS.keys())
        raise KeyError(
            f"City '{city}' is not supported. "
            f"Supported cities: {supported}"
        )
    return CITY_COORDS[city]
