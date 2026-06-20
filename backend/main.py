"""
backend/main.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PURPOSE
───────
Application entry point and wiring module for the SolarIQ backend.

Responsibilities (exhaustive):
  1. Create the FastAPI application with project metadata.
  2. Configure structured logging.
  3. Define the lifespan handler — calls DataLoader.load() exactly once
     at startup; yields control to the server; no shutdown work needed.
  4. Register CORSMiddleware.
  5. Register all five API routers.
  6. Define the GET / root endpoint.

Nothing else. No business logic, no calculations, no CSV parsing, no pandas,
no service instantiation (services construct their singletons at import time).

STARTUP BEHAVIOUR
─────────────────
  DataLoader.load() is called inside the lifespan startup block. If loading
  fails (missing CSV, schema mismatch, null values), DataLoaderError is
  logged and re-raised — the server process exits immediately rather than
  starting in a broken state.

LOCATION
────────
  backend/main.py

RUN
───
  Development:
      uvicorn main:app --reload --host 0.0.0.0 --port 8000

  Production (Render):
      uvicorn main:app --host 0.0.0.0 --port $PORT

ENVIRONMENT VARIABLES
─────────────────────
  FRONTEND_URL   — production Vercel URL added to CORS allowed origins.
                   Optional; defaults are localhost only when not set.
                   Example: https://solariq.vercel.app
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.advisor     import advisor_router
from api.cities      import cities_router
from api.health      import health_router
from api.methodology import methodology_router
from api.readiness   import readiness_router
from data.data_loader import loader
from utils.exceptions import DataLoaderError

# ─────────────────────────────────────────────────────────────────────────────
# Logging
# Configured before the app is created so startup log lines are captured.
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# CSV paths
# Resolved relative to this file's directory (backend/) so the paths are
# correct whether the server is started from backend/ or from the repo root.
# ─────────────────────────────────────────────────────────────────────────────

_HERE = os.path.dirname(os.path.abspath(__file__))
_SDSF_PATH    = os.path.join(_HERE, "data", "sdsf_city_dashboard.csv")
_ADVISOR_PATH = os.path.join(_HERE, "data", "solar_investment_advisor_results.csv")

# ─────────────────────────────────────────────────────────────────────────────
# CORS origins
# Localhost entries cover Vite (5173) and CRA (3000) development servers.
# The production Vercel URL is read from the FRONTEND_URL environment
# variable — add it to Render's environment config before going live.
# ─────────────────────────────────────────────────────────────────────────────

_LOCALHOST_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

_PRODUCTION_ORIGIN: str | None = os.getenv("FRONTEND_URL")

_ALLOWED_ORIGINS: list[str] = (
    _LOCALHOST_ORIGINS + [_PRODUCTION_ORIGIN]
    if _PRODUCTION_ORIGIN
    else _LOCALHOST_ORIGINS
)

# ─────────────────────────────────────────────────────────────────────────────
# Lifespan
# ─────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """
    FastAPI lifespan handler.

    Startup (before yield):
      Load both CSV datasets into memory. If loading fails, DataLoaderError
      is logged and re-raised — the server exits rather than starting broken.

    Shutdown (after yield):
      No cleanup required. CSV data lives in-memory and is released when
      the process exits.
    """
    # ── Startup ──────────────────────────────────────────────────────────────
    logger.info("SolarIQ backend starting up.")
    logger.info("Loading SDSF data from: %s", _SDSF_PATH)
    logger.info("Loading Advisor data from: %s", _ADVISOR_PATH)

    try:
        loader.load(_SDSF_PATH, _ADVISOR_PATH)
    except DataLoaderError as exc:
        logger.critical(
            "DataLoaderError during startup — server will not start. Detail: %s", exc
        )
        raise  # re-raise; uvicorn exits immediately

    logger.info(
        "Data loaded successfully. %d cities indexed. Server is ready.",
        len(loader.city_list()),
    )

    yield  # ── server is live here ──

    # ── Shutdown ─────────────────────────────────────────────────────────────
    logger.info("SolarIQ backend shutting down.")


# ─────────────────────────────────────────────────────────────────────────────
# Application
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="SolarIQ — AI-Powered Residential Solar Investment Advisor",
    description=(
        "Backend API for the AI-Powered Residential Solar Investment Advisor, "
        "a dissertation research project applying explainable machine learning "
        "to residential solar investment decisions across 15 Indian cities. "
        "\n\n"
        "**Research frameworks:**\n"
        "- **SDSF** (Solar Decision Support Framework) — XGBoost + SHAP, Notebook 11\n"
        "- **RSIA** (Residential Solar Investment Advisor) — NB12\n"
        "\n\n"
        "**Data:** NASA POWER meteorological data, 2019–2024, 15 Indian cities.\n\n"
        "**Model:** XGBoost with SHAP explainability (global R² = 0.8831)."
    ),
    version="1.0.0",
    contact={
        "name": "SolarIQ Research Project",
    },
    license_info={
        "name": "Academic Research — Not for commercial use",
    },
    lifespan=lifespan,
)

# ─────────────────────────────────────────────────────────────────────────────
# CORS middleware
# Registered before routers so CORS headers are applied to all responses,
# including 4xx and 5xx error responses.
# ─────────────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("CORS configured for origins: %s", _ALLOWED_ORIGINS)

# ─────────────────────────────────────────────────────────────────────────────
# Routers
# ─────────────────────────────────────────────────────────────────────────────

app.include_router(health_router)
app.include_router(cities_router)
app.include_router(readiness_router)
app.include_router(advisor_router)
app.include_router(methodology_router)

# ─────────────────────────────────────────────────────────────────────────────
# Root endpoint
# ─────────────────────────────────────────────────────────────────────────────

@app.get(
    "/",
    summary="API root",
    description="Returns API identity, version, and available endpoint listing.",
    response_description="API metadata and endpoint index.",
    tags=["Root"],
)
def get_root() -> dict[str, Any]:
    """Return API identity and available endpoints."""
    return {
        "message": "SolarIQ — AI-Powered Residential Solar Investment Advisor API",
        "version": "1.0.0",
        "status": "operational",
        "available_endpoints": {
            "GET  /health":           "API liveness check",
            "GET  /cities":           "List all 15 supported cities",
            "GET  /readiness/{city}": "Solar Decision Support Framework outputs for a city",
            "POST /advisor":          "Personalised residential solar investment assessment",
            "GET  /methodology":      "Research framework metadata",
            "GET  /docs":             "Interactive API documentation (Swagger UI)",
            "GET  /redoc":            "API documentation (ReDoc)",
        },
    }
