/**
 * api.js
 * Thin Axios wrapper for the Solar GHI FastAPI backend.
 *
 * Endpoints:
 *   GET  /health          → { status, model, n_features, xgboost_test_r2, … }
 *   GET  /test-predict    → smoke-test (legacy, kept for debug)
 *   GET  /cities          → { cities: string[], count: number }
 *   GET  /weather/{city}  → live weather snapshot
 *   POST /predict         → { predicted_ghi, city, date, weather_snapshot, … }
 */

import axios from 'axios'

const BASE = import.meta.env.VITE_API_BASE ?? '/api'

const http = axios.create({
  baseURL: BASE,
  timeout: 15_000,
  headers: { 'Content-Type': 'application/json' },
})

// ─── interceptors ────────────────────────────────────────────────────────────
http.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const msg =
      err?.response?.data?.detail ??
      err?.response?.data?.message ??
      err.message ??
      'Unknown error'
    return Promise.reject(new Error(msg))
  }
)

// ─── public API ──────────────────────────────────────────────────────────────

/**
 * Liveness probe — surfaces model metadata.
 * @returns {{ status, model, n_features, xgboost_test_r2, xgboost_test_rmse,
 *             xgboost_test_mape, train_years, test_years }}
 */
export const fetchHealth = () => http.get('/health')

/**
 * Legacy smoke-test endpoint. Kept for backend debug use.
 * @returns {{ status, city, day_of_year, dummy_features, prediction }}
 */
export const fetchTestPredict = () => http.get('/test-predict')

/**
 * Fetch the list of supported cities.
 * @returns {{ cities: string[], count: number }}
 */
export const fetchCities = () => http.get('/cities')

/**
 * Production inference endpoint.
 * Fetches live weather for the given city+date, builds the 31-feature vector,
 * and returns XGBoost GHI prediction.
 *
 * @param {string} city  - One of the 15 supported Indian city names.
 * @param {string} date  - ISO date string, e.g. "2024-06-15".
 * @returns {{
 *   predicted_ghi: number,
 *   city: string,
 *   date: string,
 *   features_used: Record<string, number>,
 *   weather_snapshot: {
 *     T2M_MAX: number, TEMP_RANGE: number, RH2M: number,
 *     PS: number, WS10M: number, CLOUD_AMT: number, PRECTOTCORR: number
 *   },
 *   lag_strategy: string,
 *   model_type: string,
 *   n_features: number,
 * }}
 */
export const fetchPredict = (city, date) =>
  http.post('/predict', { city, date })

export const fetchPredictExplain = (city, date) =>
  http.post('/predict-explain', { city, date })