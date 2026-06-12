"""
main.py
-------
FastAPI application entry-point for the Climate-Driven Solar Energy Analytics
backend.

Startup sequence
~~~~~~~~~~~~~~~~
1. Load XGBoost model      (models/xgboost_model.pkl)
2. Load StandardScaler     (models/scaler_extended.pkl)
3. Read feature list       (models/nb08_meta.json)
4. Initialise TreeExplainer (shap — new, deferred import, non-fatal if absent)

Endpoints
~~~~~~~~~
GET  /health              — liveness check; confirms artefacts are loaded
GET  /test-predict        — smoke-test: inference on a hardcoded Bengaluru vector
GET  /cities              — list of all 15 supported cities
GET  /weather/{city}      — live weather snapshot for a city (today's date)
POST /predict             — main inference endpoint: {city, date} → predicted_ghi
POST /predict-explain     — NEW: same as /predict + SHAP feature attributions
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import date as Date

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import (
    CitiesResponse,
    ExplainResponse,          # new
    PredictRequest,
    PredictResponse,
    WeatherSnapshot,
)
from services.cities import SUPPORTED_CITIES
from services.feature_builder import build_features
from services.predictor import (
    get_feature_list,
    get_meta,
    get_prediction_explanation,   # new
    load_artefacts,
    predict,
)
from services.weather_service import fetch_weather

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan — load artefacts once at startup
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=== Solar GHI backend starting up ===")
    try:
        load_artefacts()          # now also initialises SHAP TreeExplainer
        logger.info("All artefacts loaded successfully.")
    except Exception as exc:
        logger.exception("Failed to load artefacts: %s", exc)
        raise
    yield
    logger.info("=== Solar GHI backend shutting down ===")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Solar GHI Prediction API",
    description=(
        "Climate-Driven Solar Energy Analytics — XGBoost inference backend.\n\n"
        "Model: XGBoost | R² = 0.8831 | RMSE = 0.4941 | MAPE = 9.71 %\n\n"
        "POST /predict-explain returns real-time SHAP feature attributions."
    ),
    version="1.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routes — existing, unchanged
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Meta"])
def health() -> dict:
    """Liveness probe."""
    features = get_feature_list()
    if not features:
        raise HTTPException(status_code=503, detail="Artefacts not loaded.")
    meta = get_meta()
    return {
        "status":            "ok",
        "model":             meta.get("best_model_overall", "unknown"),
        "n_features":        len(features),
        "xgboost_test_r2":   meta.get("xgboost_test_r2"),
        "xgboost_test_rmse": meta.get("xgboost_test_rmse"),
        "xgboost_test_mape": meta.get("xgboost_test_mape"),
        "train_years":       meta.get("train_years"),
        "test_years":        meta.get("test_years"),
    }


@app.get("/test-predict", tags=["Debug"])
def test_predict() -> dict:
    """Smoke-test endpoint — inference on a synthetic Bengaluru vector."""
    feature_list = get_feature_list()

    dummy_values: dict[str, float] = {
        "T2M_MAX":       32.0,
        "TEMP_RANGE":     8.0,
        "RH2M":          55.0,
        "PS":            98.5,
        "WS10M":          3.2,
        "CLOUD_AMT":     20.0,
        "log1p_PREC":     0.0,
        "WIND_CLOUD":    64.0,
        "MONTH_SIN":      1.0,
        "MONTH_COS":      0.0,
        "IS_MONSOON":     0.0,
        "DAY_OF_YEAR":  172.0,
        "GHI_LAG1":       5.8,
        "RH2M_LAG1":     57.0,
        "CLOUD_LAG1":    22.0,
        "GHI_7DAY_MEAN":  5.5,
    }

    for col in feature_list[16:]:
        dummy_values[col] = 0.0
    dummy_values["CITY_Bengaluru"] = 1.0

    vector = [dummy_values[feat] for feat in feature_list]

    try:
        result = predict(vector)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return {
        "status": "ok",
        "note":   "Dummy input — not a real weather observation.",
        "city":   "Bengaluru",
        "day_of_year": int(dummy_values["DAY_OF_YEAR"]),
        "dummy_features": {feat: vector[i] for i, feat in enumerate(feature_list)},
        "prediction": result,
    }


@app.get("/cities", response_model=CitiesResponse, tags=["Meta"])
def cities() -> CitiesResponse:
    """Return the list of all 15 supported Indian cities."""
    sorted_cities = sorted(SUPPORTED_CITIES)
    return CitiesResponse(cities=sorted_cities, count=len(sorted_cities))


@app.get("/weather/{city}", tags=["Data"])
async def weather_snapshot(city: str) -> dict:
    """Fetch today's weather for *city* from Open-Meteo."""
    if city not in SUPPORTED_CITIES:
        raise HTTPException(
            status_code=422,
            detail=f"'{city}' is not a supported city. Supported: {sorted(SUPPORTED_CITIES)}",
        )
    today = Date.today()
    try:
        weather = await fetch_weather(city, today)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Open-Meteo returned HTTP {exc.response.status_code}: {exc.response.text}",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {"city": city, "date": str(today), "weather": weather}


@app.post("/predict", response_model=PredictResponse, tags=["Inference"])
async def predict_ghi(request: PredictRequest) -> PredictResponse:
    """Main production inference endpoint — UNCHANGED.

    Accepts {city, date} → fetches weather → builds features → XGBoost → GHI.
    """
    city       = request.city
    query_date = request.date

    try:
        weather = await fetch_weather(city, query_date)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                f"Open-Meteo returned HTTP {exc.response.status_code} for "
                f"city={city} date={query_date}. Response: {exc.response.text[:300]}"
            ),
        )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Open-Meteo request timed out.")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Weather fetch failed: {exc}")

    try:
        vector, feature_dict = build_features(city, query_date, weather)
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=f"Feature engineering failed: {exc}")

    try:
        result = predict(vector)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=500, detail=f"Model inference failed: {exc}")

    snapshot = WeatherSnapshot(
        T2M_MAX=weather["T2M_MAX"],
        TEMP_RANGE=weather["TEMP_RANGE"],
        RH2M=weather["RH2M"],
        PS=weather["PS"],
        WS10M=weather["WS10M"],
        CLOUD_AMT=weather["CLOUD_AMT"],
        PRECTOTCORR=weather["PRECTOTCORR"],
    )

    return PredictResponse(
        predicted_ghi=result["predicted_ghi"],
        city=city,
        date=str(query_date),
        features_used=feature_dict,
        weather_snapshot=snapshot,
        lag_strategy="climatological_defaults",
        model_type=result["model_type"],
        n_features=result["n_features"],
    )


# ---------------------------------------------------------------------------
# NEW endpoint — POST /predict-explain
# ---------------------------------------------------------------------------

@app.post("/predict-explain", response_model=ExplainResponse, tags=["Inference"])
async def predict_ghi_explain(request: PredictRequest) -> ExplainResponse:
    """GHI prediction with real-time SHAP feature attributions.

    Identical weather-fetch and feature-engineering pipeline as POST /predict,
    then computes SHAP values using the singleton TreeExplainer initialised at
    startup.

    The SHAP explanation identifies which climate features drove the model's
    prediction above or below its baseline (expected training output).

    Request body
    ~~~~~~~~~~~~
    Same as POST /predict: ``{ "city": "Bengaluru", "date": "2024-06-15" }``

    Response — ExplainResponse
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    predicted_ghi           float   — GHI in kWh/m²/day
    base_value              float   — model mean output (SHAP baseline)
    prediction_delta        float   — predicted_ghi − base_value
    top_positive_features   list    — top-5 climate features pushing GHI UP
    top_negative_features   list    — top-5 climate features pulling GHI DOWN
    feature_shap_values     dict    — all 31 SHAP values (for client charts)
    shap_error              str?    — set only if SHAP computation fails

    Graceful degradation
    ~~~~~~~~~~~~~~~~~~~~
    If the shap package is not installed or computation fails, the endpoint
    returns HTTP 200 with predicted_ghi populated and shap_error set.
    It never returns 500 for SHAP failures alone.
    """
    city       = request.city
    query_date = request.date

    # ── Step 1: Fetch weather ─────────────────────────────────────────────────
    try:
        weather = await fetch_weather(city, query_date)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                f"Open-Meteo returned HTTP {exc.response.status_code} for "
                f"city={city} date={query_date}. Response: {exc.response.text[:300]}"
            ),
        )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Open-Meteo request timed out.")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Weather fetch failed: {exc}")

    # ── Step 2: Build feature vector ──────────────────────────────────────────
    try:
        vector, feature_dict = build_features(city, query_date, weather)
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=f"Feature engineering failed: {exc}")

    # ── Step 3: Predict + SHAP (single call, graceful on SHAP failure) ────────
    try:
        explanation = get_prediction_explanation(vector, feature_dict)
    except (ValueError, RuntimeError) as exc:
        # Only hard-fail on missing artefacts or feature-count mismatch.
        # SHAP-specific errors are caught inside get_prediction_explanation.
        raise HTTPException(status_code=500, detail=f"Inference failed: {exc}")

    # ── Step 4: Assemble response ─────────────────────────────────────────────
    snapshot = WeatherSnapshot(
        T2M_MAX=weather["T2M_MAX"],
        TEMP_RANGE=weather["TEMP_RANGE"],
        RH2M=weather["RH2M"],
        PS=weather["PS"],
        WS10M=weather["WS10M"],
        CLOUD_AMT=weather["CLOUD_AMT"],
        PRECTOTCORR=weather["PRECTOTCORR"],
    )

    return ExplainResponse(
        # Core prediction
        predicted_ghi    = explanation["predicted_ghi"],
        city             = city,
        date             = str(query_date),
        model_type       = "XGBRegressor",
        n_features       = len(vector),
        weather_snapshot = snapshot,
        lag_strategy     = "climatological_defaults",
        features_used    = feature_dict,
        # SHAP fields (None / empty on failure)
        base_value             = explanation.get("base_value"),
        prediction_delta       = explanation.get("prediction_delta"),
        top_positive_features  = explanation.get("top_positive_features", []),
        top_negative_features  = explanation.get("top_negative_features", []),
        feature_shap_values    = explanation.get("feature_shap_values", {}),
        shap_error             = explanation.get("shap_error"),
    )
