# Viva Preparation Notes

## Project in 30 Seconds

This project develops an AI-powered Residential Solar Investment Advisor using explainable machine learning.

An XGBoost model predicts solar irradiance using NASA POWER weather data.

SHAP is used to explain model predictions.

The Solar Decision Support Framework evaluates reliability, confidence, and solar suitability.

These outputs are then used by the Residential Solar Investment Advisor to estimate system size, annual generation, savings, payback period, and investment feasibility.

The final result is an explainable recommendation for residential solar adoption.

---

# Expected Viva Questions

## Why XGBoost?

Reasons:

- Strong performance on tabular data.
- Handles nonlinear relationships.
- Robust against overfitting.
- Widely used in solar forecasting literature.
- Outperformed alternative baseline models during experimentation.

---

## Why SHAP?

Reasons:

- Provides local and global explainability.
- Shows feature contributions.
- More informative than standard feature importance.
- Improves user trust.

---

## Why Reliability Score?

Predicted GHI alone is insufficient.

A city may have high average irradiance but high variability.

Reliability Score captures long-term consistency.

---

## Why Prediction Confidence?

Predictions should not be interpreted without uncertainty information.

Confidence provides transparency regarding forecast quality.

---

## Why Suitability Framework?

Homeowners need interpretable decisions rather than raw meteorological values.

The framework converts technical outputs into actionable guidance.

---

## Why Investment Advisor?

Most users care about:

- Savings
- Payback
- Return on Investment

rather than weather metrics.

The Investment Advisor bridges this gap.

---

## Key Research Contributions

1. Explainable GHI prediction.
2. Reliability-aware solar assessment.
3. Solar Decision Support Framework.
4. Residential Solar Investment Advisor.
5. Explainable recommendation system.

---

# Limitations

- Limited geographic scope.
- Historical data only.
- No real-world installation validation.
- Assumption-based economic analysis.

---

# Future Work

- Real-time weather integration.
- Dynamic tariff integration.
- Rooftop image processing.
- Nationwide deployment.
- Mobile application.
