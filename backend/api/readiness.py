"""
backend/api/readiness.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PURPOSE
───────
Route handler for GET /readiness/{city}.

Returns the complete Solar Decision Support Framework (SDSF / NB11) outputs
for a single city: GHI percentiles, Reliability Score, Prediction Confidence,
Suitability classification, and plain-language explanation.

Accepts both canonical city names ("Bengaluru") and URL slugs ("bengaluru").
Resolution is handled inside ReadinessService — this route passes the raw
path parameter through unchanged.

Delegates entirely to ReadinessService.get_readiness(city).

LOCATION
────────
  backend/api/readiness.py

REGISTERED IN
─────────────
  backend/main.py  →  app.include_router(readiness_router)
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from schemas.readiness_response import ReadinessResponse
from services.readiness_service import readiness_service
from utils.exceptions import CityNotFoundError, DataLoaderError

logger = logging.getLogger(__name__)

readiness_router = APIRouter(tags=["Solar Readiness"])


@readiness_router.get(
    "/readiness/{city}",
    response_model=ReadinessResponse,
    status_code=200,
    summary="Solar readiness for a city",
    description=(
        "Returns Solar Decision Support Framework (SDSF) outputs for the requested "
        "city. Outputs are frozen research results from Notebook 11 — they are never "
        "recomputed at request time. "
        "\n\n"
        "The `city` path parameter accepts both the canonical city name "
        "(e.g. `Bengaluru`) and its URL slug (e.g. `bengaluru`). "
        "\n\n"
        "**Fields returned:** Mean GHI, P10/P50/P90 GHI, Reliability Score, "
        "RS Category, Model RMSE, Model MAPE, Prediction Confidence, "
        "Suitability classification, and plain-language explanation."
    ),
    response_description=(
        "SDSF outputs for the requested city including GHI metrics, "
        "Reliability Score, Prediction Confidence, and Suitability classification."
    ),
    responses={
        404: {"description": "City not found or not supported."},
        500: {"description": "Data layer initialisation failure."},
    },
)
def get_readiness(city: str) -> ReadinessResponse:
    """Return SDSF outputs for a single city."""
    try:
        return readiness_service.get_readiness(city)
    except CityNotFoundError as exc:
        logger.info("[readiness] CityNotFoundError for %r: %s", city, exc)
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except DataLoaderError as exc:
        logger.error("[readiness] DataLoaderError: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Solar readiness data is unavailable. The data layer failed to initialise.",
        ) from exc
