"""
schemas.py
----------
Pydantic v2 request and response models for the Solar GHI Prediction API.

Changes in this revision
~~~~~~~~~~~~~~~~~~~~~~~~
* SHAPFeatureContribution  — new model for a single ranked feature entry
* ExplainResponse          — new response model for POST /predict-explain
* PredictRequest is reused as-is for /predict-explain (same body shape)
* All existing models (PredictRequest, PredictResponse, WeatherSnapshot,
  CitiesResponse) are UNCHANGED — frontend compatibility is preserved.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Request  (unchanged)
# ---------------------------------------------------------------------------

class PredictRequest(BaseModel):
    """Body for POST /predict and POST /predict-explain."""

    city: Annotated[
        str,
        Field(
            description=(
                "Name of the Indian city for which to predict GHI. "
                "Must be one of the 15 cities supported by the model."
            ),
            examples=["Bengaluru", "Delhi", "Mumbai"],
        ),
    ]

    date: Annotated[
        date,
        Field(
            description=(
                "Calendar date for the prediction (YYYY-MM-DD). "
                "The Open-Meteo historical weather API supports dates from "
                "1940-01-01 to ~5 days after today. Future dates are not "
                "supported."
            ),
            examples=["2024-06-15"],
        ),
    ]

    @field_validator("city")
    @classmethod
    def city_must_be_supported(cls, v: str) -> str:
        from services.cities import SUPPORTED_CITIES
        if v not in SUPPORTED_CITIES:
            raise ValueError(
                f"'{v}' is not a supported city. "
                f"Supported: {sorted(SUPPORTED_CITIES)}"
            )
        return v

    @field_validator("date")
    @classmethod
    def date_not_in_future(cls, v: date) -> date:
        today = datetime.utcnow().date()
        if v > today:
            raise ValueError(
                f"Date '{v}' is in the future. "
                "Only past or present dates are supported."
            )
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "city": "Bengaluru",
                "date": "2024-06-15",
            }
        }
    }


# ---------------------------------------------------------------------------
# Shared sub-models  (unchanged)
# ---------------------------------------------------------------------------

class WeatherSnapshot(BaseModel):
    """Raw weather values fetched from Open-Meteo (before feature engineering)."""

    T2M_MAX:     float = Field(description="Maximum 2m temperature (°C)")
    TEMP_RANGE:  float = Field(description="Diurnal temperature range (°C)")
    RH2M:        float = Field(description="Relative humidity at 2m (%)")
    PS:          float = Field(description="Surface pressure (kPa)")
    WS10M:       float = Field(description="Wind speed at 10m (m/s)")
    CLOUD_AMT:   float = Field(description="Total cloud cover (%)")
    PRECTOTCORR: float = Field(description="Precipitation (mm/day)")


# ---------------------------------------------------------------------------
# Existing response  (unchanged)
# ---------------------------------------------------------------------------

class PredictResponse(BaseModel):
    """Response from POST /predict — unchanged, frontend-compatible."""

    predicted_ghi:    float             = Field(description="Predicted GHI (kWh/m²/day)", examples=[5.87])
    city:             str               = Field(description="City name as supplied in the request")
    date:             str               = Field(description="Date as supplied in the request (YYYY-MM-DD)")
    features_used:    dict[str, float]  = Field(description="All 31 features passed to the model")
    weather_snapshot: WeatherSnapshot   = Field(description="Raw Open-Meteo values before feature engineering")
    lag_strategy:     str               = Field(default="climatological_defaults")
    model_type:       str               = Field(description="Class name of the loaded ML model")
    n_features:       int               = Field(description="Number of features used for inference (must be 31)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "predicted_ghi": 5.87,
                "city": "Bengaluru",
                "date": "2024-06-15",
                "features_used": {"T2M_MAX": 30.2, "CLOUD_AMT": 18.0},
                "weather_snapshot": {
                    "T2M_MAX": 30.2, "TEMP_RANGE": 10.1,
                    "RH2M": 64.0, "PS": 91.5,
                    "WS10M": 2.8, "CLOUD_AMT": 18.0, "PRECTOTCORR": 0.0,
                },
                "lag_strategy": "climatological_defaults",
                "model_type": "XGBRegressor",
                "n_features": 31,
            }
        }
    }


# ---------------------------------------------------------------------------
# NEW — SHAP sub-models
# ---------------------------------------------------------------------------

class SHAPFeatureContribution(BaseModel):
    """A single feature's SHAP contribution to a prediction.

    Appears in the top_positive_features and top_negative_features lists
    inside ExplainResponse.
    """

    feature:       str   = Field(description="Feature name (e.g. 'CLOUD_AMT')")
    shap_value:    float = Field(
        description=(
            "SHAP value for this feature on this prediction. "
            "Positive = pushes GHI above base_value; "
            "Negative = pulls GHI below base_value. "
            "Units: kWh/m²/day."
        )
    )
    feature_value: float = Field(
        description="Raw (unscaled) value of this feature for this prediction"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "feature":       "CLOUD_AMT",
                "shap_value":    -0.8231,
                "feature_value": 72.4,
            }
        }
    }


# ---------------------------------------------------------------------------
# NEW — ExplainResponse
# ---------------------------------------------------------------------------

class ExplainResponse(BaseModel):
    """Response from POST /predict-explain.

    Contains the full GHI prediction plus SHAP-based feature attributions.
    City one-hot features are present in feature_shap_values but excluded
    from the top-N ranked lists so that interpretable climate drivers are
    surfaced to the user.

    Graceful degradation
    ~~~~~~~~~~~~~~~~~~~~
    If the SHAP library is not installed or computation fails, the response
    still contains predicted_ghi, city, date, and weather_snapshot.
    The SHAP fields will be empty / None, and shap_error will be populated
    with a human-readable explanation.
    """

    # ── Core prediction (always present) ─────────────────────────────────────
    predicted_ghi:    float           = Field(description="Predicted GHI (kWh/m²/day)", examples=[5.87])
    city:             str             = Field(description="City name")
    date:             str             = Field(description="Date (YYYY-MM-DD)")
    model_type:       str             = Field(description="Class name of the loaded ML model")
    n_features:       int             = Field(description="Number of features used (31)")
    weather_snapshot: WeatherSnapshot = Field(description="Raw weather values from Open-Meteo")
    lag_strategy:     str             = Field(default="climatological_defaults")
    features_used:    dict[str, float]= Field(description="Full 31-feature dict passed to the model")

    # ── SHAP explanation (present when shap is installed and succeeds) ────────
    base_value: Optional[float] = Field(
        default=None,
        description=(
            "SHAP expected value — the model's mean training output. "
            "base_value + sum(all shap_values) ≈ predicted_ghi."
        ),
    )
    prediction_delta: Optional[float] = Field(
        default=None,
        description="predicted_ghi − base_value: total attribution from all features combined",
    )
    top_positive_features: list[SHAPFeatureContribution] = Field(
        default_factory=list,
        description=(
            "Up to 5 non-city features with the largest positive SHAP values "
            "(features that pushed GHI higher than the baseline)."
        ),
    )
    top_negative_features: list[SHAPFeatureContribution] = Field(
        default_factory=list,
        description=(
            "Up to 5 non-city features with the largest negative SHAP values "
            "(features that suppressed GHI below the baseline)."
        ),
    )
    feature_shap_values: dict[str, float] = Field(
        default_factory=dict,
        description=(
            "All 31 SHAP values keyed by feature name, including city one-hots. "
            "Suitable for building a full waterfall chart on the client side."
        ),
    )

    # ── Error field (set only on SHAP failure) ────────────────────────────────
    shap_error: Optional[str] = Field(
        default=None,
        description=(
            "Human-readable error message when SHAP computation fails. "
            "When None, SHAP computation succeeded."
        ),
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "predicted_ghi":   5.87,
                "city":            "Bengaluru",
                "date":            "2024-06-15",
                "model_type":      "XGBRegressor",
                "n_features":      31,
                "weather_snapshot": {
                    "T2M_MAX": 30.2, "TEMP_RANGE": 10.1, "RH2M": 64.0,
                    "PS": 91.5, "WS10M": 2.8, "CLOUD_AMT": 18.0, "PRECTOTCORR": 0.0,
                },
                "lag_strategy": "climatological_defaults",
                "features_used": {"T2M_MAX": 30.2, "CLOUD_AMT": 18.0},
                "base_value":         4.312,
                "prediction_delta":   1.558,
                "top_positive_features": [
                    {"feature": "GHI_7DAY_MEAN", "shap_value":  0.721, "feature_value": 5.5},
                    {"feature": "T2M_MAX",        "shap_value":  0.512, "feature_value": 30.2},
                    {"feature": "IS_MONSOON",     "shap_value":  0.201, "feature_value": 0.0},
                    {"feature": "DAY_OF_YEAR",    "shap_value":  0.124, "feature_value": 167.0},
                ],
                "top_negative_features": [
                    {"feature": "CLOUD_AMT",  "shap_value": -0.823, "feature_value": 18.0},
                    {"feature": "RH2M",       "shap_value": -0.411, "feature_value": 64.0},
                    {"feature": "log1p_PREC", "shap_value": -0.098, "feature_value": 0.0},
                ],
                "feature_shap_values": {
                    "CLOUD_AMT": -0.823, "T2M_MAX": 0.512, "CITY_Bengaluru": 0.102,
                },
                "shap_error": None,
            }
        }
    }


# ---------------------------------------------------------------------------
# City list response  (unchanged)
# ---------------------------------------------------------------------------

class CitiesResponse(BaseModel):
    """Response from GET /cities."""

    cities: list[str] = Field(description="Alphabetically sorted list of supported city names")
    count:  int        = Field(description="Number of supported cities")
