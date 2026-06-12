"""
predictor.py
------------
Loads the XGBoost model, StandardScaler, and SHAP TreeExplainer at startup.
Exposes two public functions used by the API routes:

  predict(feature_vector)               — existing, unchanged
  get_prediction_explanation(feature_vector, feature_dict) — new SHAP function

SHAP design decisions
~~~~~~~~~~~~~~~~~~~~~
* TreeExplainer is initialised once in load_artefacts() and stored as a
  module-level singleton (_explainer).  XGBoost's native tree-path algorithm
  makes per-request computation ~1 ms — no caching or batching needed.

* SHAP values are computed on the SAME X_scaled array that XGBoost sees,
  satisfying the requirement that explanations are consistent with predictions.

* TreeExplainer does NOT require background data for XGBoost regressors;
  it uses the exact tree-path (interventional) algorithm.  This means
  base_value == expected_value, a scalar float, which is stable across calls.

* All SHAP errors are caught and surfaced as a structured ExplainError dict
  so the /predict-explain endpoint degrades gracefully without killing the
  process or breaking /predict.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import joblib
import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_MODELS_DIR  = Path(__file__).resolve().parent.parent / "models"
_MODEL_PATH  = _MODELS_DIR / "xgboost_model.pkl"
_SCALER_PATH = _MODELS_DIR / "scaler_extended.pkl"
_META_PATH   = _MODELS_DIR / "nb08_meta.json"

# ---------------------------------------------------------------------------
# Module-level singletons
# ---------------------------------------------------------------------------
_model        = None
_scaler       = None
_explainer    = None          # shap.TreeExplainer — new
_feature_list: list[str] = []
_meta: dict[str, Any]    = {}


# ---------------------------------------------------------------------------
# Startup loader
# ---------------------------------------------------------------------------

def load_artefacts() -> None:
    """Load model, scaler, metadata, and SHAP explainer from disk.

    Called exactly once from the FastAPI lifespan hook.  All objects are stored
    as module-level singletons so no re-loading occurs per request.
    """
    global _model, _scaler, _explainer, _feature_list, _meta

    # ── 1. Model ──────────────────────────────────────────────────────────────
    logger.info("Loading XGBoost model from %s", _MODEL_PATH)
    _model = joblib.load(_MODEL_PATH)
    logger.info("Model loaded: %s", type(_model).__name__)

    # ── 2. Scaler ─────────────────────────────────────────────────────────────
    logger.info("Loading StandardScaler from %s", _SCALER_PATH)
    _scaler = joblib.load(_SCALER_PATH)
    logger.info("Scaler loaded: %s | n_features=%d", type(_scaler).__name__, _scaler.n_features_in_)

    # ── 3. Metadata ───────────────────────────────────────────────────────────
    logger.info("Loading metadata from %s", _META_PATH)
    with open(_META_PATH, "r", encoding="utf-8") as fh:
        _meta = json.load(fh)
    _feature_list = _meta["feature_list"]
    logger.info("Feature list: %d features", len(_feature_list))

    # ── 4. SHAP TreeExplainer (new) ───────────────────────────────────────────
    # Import is deferred so the rest of the app still starts if shap is absent.
    # TreeExplainer for XGBoost uses the exact tree-path algorithm; no
    # background data is required and base_value is a stable scalar.
    try:
        import shap  # noqa: F401 — version logged below
        logger.info("shap version: %s", shap.__version__)

        _explainer = shap.TreeExplainer(_model)
        logger.info(
            "SHAP TreeExplainer initialised | base_value=%.4f",
            float(_explainer.expected_value)
            if not hasattr(_explainer.expected_value, "__len__")
            else float(_explainer.expected_value[0]),
        )
    except ImportError:
        logger.warning(
            "shap package not installed — /predict-explain will return a "
            "graceful error. Install with: pip install shap"
        )
        _explainer = None
    except Exception as exc:
        logger.error("SHAP TreeExplainer failed to initialise: %s", exc)
        _explainer = None


# ---------------------------------------------------------------------------
# Public helpers — existing, unchanged
# ---------------------------------------------------------------------------

def get_feature_list() -> list[str]:
    """Return the ordered feature list expected by the model."""
    return _feature_list


def get_meta() -> dict[str, Any]:
    """Return the full metadata dictionary from nb08_meta.json."""
    return _meta


def predict(feature_vector: list[float]) -> dict[str, Any]:
    """Scale *feature_vector* and run XGBoost inference.

    Parameters
    ----------
    feature_vector:
        Ordered list of exactly 31 numeric values.

    Returns
    -------
    dict with keys: predicted_ghi, n_features, model_type
    """
    if _model is None or _scaler is None:
        raise RuntimeError("Artefacts not loaded — call load_artefacts() first.")

    n_expected = len(_feature_list)
    n_received = len(feature_vector)
    if n_received != n_expected:
        raise ValueError(
            f"Feature count mismatch: expected {n_expected}, got {n_received}."
        )

    X        = np.array(feature_vector, dtype=np.float64).reshape(1, -1)
    X_scaled = _scaler.transform(X)
    prediction = float(_model.predict(X_scaled)[0])

    return {
        "predicted_ghi": round(prediction, 4),
        "n_features":    n_received,
        "model_type":    type(_model).__name__,
    }


# ---------------------------------------------------------------------------
# New public function — SHAP explanation
# ---------------------------------------------------------------------------

def get_prediction_explanation(
    feature_vector: list[float],
    feature_dict:   dict[str, float],
) -> dict[str, Any]:
    """Compute XGBoost prediction and SHAP feature contributions.

    This function is the single source of truth for /predict-explain.
    It reuses the same _model, _scaler, and _explainer singletons loaded at
    startup — no objects are created per request.

    Parameters
    ----------
    feature_vector:
        Ordered list of 31 floats (same order as FEATURE_LIST / nb08_meta.json).
        Must be the raw (unscaled) vector — this function scales it internally
        so that SHAP values are computed on the identical array that XGBoost sees.

    feature_dict:
        Mapping of feature_name → raw feature value, returned by
        feature_builder.build_features().  Used to populate feature_value in
        the top-N contributor lists.

    Returns
    -------
    dict with the following keys:

        predicted_ghi       float   — model output (kWh/m²/day)
        base_value          float   — SHAP expected value (mean training output)
        prediction_delta    float   — predicted_ghi − base_value
        top_positive_features  list[dict]  — top-5 SHAP contributors > 0
        top_negative_features  list[dict]  — top-5 SHAP contributors < 0
        feature_shap_values dict[str, float] — all 31 SHAP values keyed by name

        On SHAP failure, returns a dict with key "shap_error" (str) plus the
        basic prediction fields so the caller can still surface a GHI value.

    Raises
    ------
    RuntimeError
        If load_artefacts() has not been called first.
    ValueError
        If feature_vector does not contain exactly 31 values.
    """
    if _model is None or _scaler is None:
        raise RuntimeError("Artefacts not loaded — call load_artefacts() first.")

    n_expected = len(_feature_list)
    n_received = len(feature_vector)
    if n_received != n_expected:
        raise ValueError(
            f"Feature count mismatch: expected {n_expected}, got {n_received}."
        )

    # ── Scale (same path as predict()) ────────────────────────────────────────
    X        = np.array(feature_vector, dtype=np.float64).reshape(1, -1)
    X_scaled = _scaler.transform(X)

    # ── XGBoost prediction ────────────────────────────────────────────────────
    predicted_ghi = round(float(_model.predict(X_scaled)[0]), 4)

    # ── SHAP explanation ──────────────────────────────────────────────────────
    if _explainer is None:
        logger.warning("SHAP explainer not available — returning prediction only.")
        return {
            "predicted_ghi":          predicted_ghi,
            "base_value":             None,
            "prediction_delta":       None,
            "top_positive_features":  [],
            "top_negative_features":  [],
            "feature_shap_values":    {},
            "shap_error": (
                "SHAP explainer is unavailable. "
                "Ensure 'shap' is installed: pip install shap"
            ),
        }

    try:
        # shap_values shape: (1, n_features) for a single-output regressor.
        # TreeExplainer.expected_value is a scalar for regressors.
        shap_values_raw = _explainer.shap_values(X_scaled)          # (1, 31)
        shap_row        = shap_values_raw[0]                        # (31,)

        # Handle edge case: some versions return (n_features,) directly
        if shap_row.ndim == 0:
            raise ValueError("Unexpected SHAP output shape — cannot unpack.")

        base_value = (
            float(_explainer.expected_value)
            if not hasattr(_explainer.expected_value, "__len__")
            else float(_explainer.expected_value[0])
        )

        # ── Build full feature → SHAP mapping ────────────────────────────────
        feature_shap: dict[str, float] = {
            feat: round(float(shap_row[i]), 6)
            for i, feat in enumerate(_feature_list)
        }

        # ── Top-5 positive and negative contributors ──────────────────────────
        # Exclude city one-hot columns from the ranked lists — they are not
        # interpretable as continuous drivers and clutter the explanation.
        # They remain in feature_shap_values for completeness.
        interpretable = [
            (feat, sv)
            for feat, sv in feature_shap.items()
            if not feat.startswith("CITY_")
        ]

        sorted_by_shap = sorted(interpretable, key=lambda x: x[1], reverse=True)

        top_positive = [
            {
                "feature":       feat,
                "shap_value":    round(sv, 6),
                "feature_value": round(float(feature_dict.get(feat, 0.0)), 4),
            }
            for feat, sv in sorted_by_shap
            if sv > 0
        ][:5]

        top_negative = [
            {
                "feature":       feat,
                "shap_value":    round(sv, 6),
                "feature_value": round(float(feature_dict.get(feat, 0.0)), 4),
            }
            for feat, sv in reversed(sorted_by_shap)
            if sv < 0
        ][:5]

        prediction_delta = round(predicted_ghi - base_value, 4)

        logger.info(
            "SHAP explanation computed | predicted_ghi=%.4f base=%.4f delta=%.4f "
            "top_pos=%s top_neg=%s",
            predicted_ghi, base_value, prediction_delta,
            [t["feature"] for t in top_positive],
            [t["feature"] for t in top_negative],
        )

        return {
            "predicted_ghi":         predicted_ghi,
            "base_value":            round(base_value, 4),
            "prediction_delta":      prediction_delta,
            "top_positive_features": top_positive,
            "top_negative_features": top_negative,
            "feature_shap_values":   feature_shap,
        }

    except Exception as exc:
        # Graceful degradation: return the GHI prediction with an error note.
        # The endpoint is still useful even if SHAP computation fails.
        logger.error("SHAP computation failed: %s", exc, exc_info=True)
        return {
            "predicted_ghi":         predicted_ghi,
            "base_value":            None,
            "prediction_delta":      None,
            "top_positive_features": [],
            "top_negative_features": [],
            "feature_shap_values":   {},
            "shap_error":            f"SHAP computation failed: {exc}",
        }
