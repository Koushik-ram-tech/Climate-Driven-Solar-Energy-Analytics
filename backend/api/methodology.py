"""
backend/api/methodology.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PURPOSE
───────
Route handler for GET /methodology.

Returns static project metadata for the How It Works and About pages:
project title, one-sentence description, and framework version.

No DataLoader dependency, no exception handling required — MethodologyService
constructs its response once at instantiation and cannot fail at runtime.

LOCATION
────────
  backend/api/methodology.py

REGISTERED IN
─────────────
  backend/main.py  →  app.include_router(methodology_router)
"""

from __future__ import annotations

from fastapi import APIRouter

from schemas.methodology_response import MethodologyResponse
from services.methodology_service import methodology_service

methodology_router = APIRouter(tags=["Methodology"])


@methodology_router.get(
    "/methodology",
    response_model=MethodologyResponse,
    status_code=200,
    summary="Framework methodology metadata",
    description=(
        "Returns static metadata describing the AI-Powered Residential Solar "
        "Investment Advisor research framework. Used by the How It Works and "
        "About pages. "
        "\n\n"
        "The response is a frozen project-level constant — it does not vary "
        "by city or user input and is constructed once at server startup."
    ),
    response_description=(
        "Project title, one-sentence methodology description, and framework version."
    ),
)
def get_methodology() -> MethodologyResponse:
    """Return the project methodology metadata."""
    return methodology_service.get_methodology()
