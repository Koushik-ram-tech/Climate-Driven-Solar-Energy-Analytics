"""
backend/api/cities.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PURPOSE
───────
Route handler for GET /cities.

Returns the list of supported city names and URL slugs.
Used by the frontend Assessment wizard city selector and any component
that needs the canonical city list for routing.

Delegates entirely to CityService.get_all_cities().

LOCATION
────────
  backend/api/cities.py

REGISTERED IN
─────────────
  backend/main.py  →  app.include_router(cities_router)
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from schemas.cities_response import CitiesResponse
from services.city_service import city_service
from utils.exceptions import DataLoaderError

logger = logging.getLogger(__name__)

cities_router = APIRouter(tags=["Cities"])


@cities_router.get(
    "/cities",
    response_model=CitiesResponse,
    status_code=200,
    summary="List supported cities",
    description=(
        "Returns the complete list of the 15 Indian cities supported by the "
        "Solar Decision Support Framework (SDSF) and the Residential Solar "
        "Investment Advisor (RSIA). Each entry includes the canonical city name "
        "and its URL-safe slug for use in subsequent API calls and frontend routes."
    ),
    response_description=(
        "Alphabetically sorted list of all 15 supported cities with their URL slugs."
    ),
)
def get_cities() -> CitiesResponse:
    """Return all supported cities."""
    try:
        return city_service.get_all_cities()
    except DataLoaderError as exc:
        logger.error("[cities] DataLoaderError: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="City data is unavailable. The data layer failed to initialise.",
        ) from exc
