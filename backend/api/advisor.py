"""
backend/api/advisor.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PURPOSE
───────
Route handler for POST /advisor.

The core endpoint of the SolarIQ backend. Accepts a validated
AdvisorRequest (city, monthly_bill, roof_area_sqft, budget) and returns
a personalised AdvisorResponse containing system sizing, financial
projections, investment recommendation, and SDSF context.

Request validation (field types, ranges, and supported city name) is
performed automatically by FastAPI via the AdvisorRequest Pydantic model
before the route function is called. This route performs no validation
itself — it delegates the complete computation to AdvisorService.

LOCATION
────────
  backend/api/advisor.py

REGISTERED IN
─────────────
  backend/main.py  →  app.include_router(advisor_router)
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from schemas.advisor_request import AdvisorRequest
from schemas.advisor_response import AdvisorResponse
from services.advisor_service import advisor_service
from utils.exceptions import (
    CalculationError,
    CityNotFoundError,
    DataLoaderError,
    InvalidAdvisorInputError,
)

logger = logging.getLogger(__name__)

advisor_router = APIRouter(tags=["Investment Advisor"])


@advisor_router.post(
    "/advisor",
    response_model=AdvisorResponse,
    status_code=200,
    summary="Personalised solar investment assessment",
    description=(
        "Runs the complete Residential Solar Investment Advisor (RSIA / NB12) "
        "workflow for a single homeowner profile and returns a personalised "
        "investment assessment. "
        "\n\n"
        "**Workflow (NB12 §5–§10):**\n"
        "1. Estimate annual electricity consumption from monthly bill\n"
        "2. Recommend system size (kW) from roof area, budget, and city GHI\n"
        "3. Estimate annual generation, Year-1 savings, and payback period\n"
        "4. Project 25-year lifetime savings with degradation and tariff escalation\n"
        "5. Generate investment recommendation (rule-based engine)\n"
        "6. Generate plain-language explanation\n"
        "\n\n"
        "**Fixed constant:** electricity tariff is set to ₹7.0/kWh and is not "
        "a user input. "
        "\n\n"
        "**SDSF context** (Suitability, Reliability Score, Prediction Confidence) "
        "is joined from the frozen NB11 outputs so the frontend "
        "EconomicsVsSuitabilityPanel can render from this single response."
    ),
    response_description=(
        "Personalised investment outputs: system size, annual generation, "
        "Year-1 savings, payback period, lifetime savings, net benefit, "
        "investment recommendation, explanation, and SDSF context."
    ),
    responses={
        400: {"description": "Invalid advisor input values."},
        404: {"description": "City not found or not supported."},
        422: {"description": "Request body validation failed (field types or ranges)."},
        500: {"description": "Calculation failure or data layer error."},
    },
)
def post_advisor(request: AdvisorRequest) -> AdvisorResponse:
    """Run the personalised solar investment workflow."""
    try:
        return advisor_service.calculate(request)
    except CityNotFoundError as exc:
        logger.info("[advisor] CityNotFoundError for city=%r: %s", request.city, exc)
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except InvalidAdvisorInputError as exc:
        logger.info("[advisor] InvalidAdvisorInputError: %s", exc)
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except CalculationError as exc:
        logger.error("[advisor] CalculationError for city=%r: %s", request.city, exc)
        raise HTTPException(
            status_code=500,
            detail=(
                "An error occurred during investment calculation. "
                f"Detail: {exc}"
            ),
        ) from exc
    except DataLoaderError as exc:
        logger.error("[advisor] DataLoaderError: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Solar data is unavailable. The data layer failed to initialise.",
        ) from exc
