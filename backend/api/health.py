"""
backend/api/health.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PURPOSE
───────
Route handler for GET /health.

Liveness check — confirms the API process is running and responding.
No service call, no DataLoader dependency, no exception handling required.
The route constructs the HealthResponse directly: the only valid value
for status is the Literal "healthy", so there is nothing to compute.

LOCATION
────────
  backend/api/health.py

REGISTERED IN
─────────────
  backend/main.py  →  app.include_router(health_router)
"""

from __future__ import annotations

from fastapi import APIRouter

from schemas.health_response import HealthResponse

health_router = APIRouter(tags=["Health"])


@health_router.get(
    "/health",
    response_model=HealthResponse,
    status_code=200,
    summary="Health check",
    description=(
        "Liveness endpoint. Returns HTTP 200 with status='healthy' whenever "
        "the API process is running. Used by deployment platforms (Render) "
        "and uptime monitors to verify the service is alive."
    ),
    response_description="API is running and healthy.",
)
def get_health() -> HealthResponse:
    """Return the API health status."""
    return HealthResponse(status="healthy")
