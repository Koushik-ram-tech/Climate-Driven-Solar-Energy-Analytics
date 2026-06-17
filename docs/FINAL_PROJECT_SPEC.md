# AI-Powered Residential Solar Investment Advisor Using Explainable Machine Learning

## Abstract

This project develops an AI-powered decision support system for residential solar investment assessment across major Indian cities. The system combines machine learning-based solar irradiance prediction, explainable AI, reliability assessment, suitability evaluation, and financial investment analysis to generate actionable recommendations for homeowners.

The project consists of two integrated frameworks:

1. Solar Decision Support Framework (SDSF)
2. Residential Solar Investment Advisor (RSIA)

---

# Problem Statement

Most existing solar calculators estimate savings using static assumptions and provide limited transparency regarding prediction reliability and uncertainty.

Homeowners often lack answers to:

- Is solar suitable for my location?
- How reliable are the predictions?
- How much should I invest?
- What payback period can I expect?
- Why is the recommendation being made?

This project addresses these gaps using explainable machine learning and decision-support frameworks.

---

# Objectives

1. Predict Global Horizontal Irradiance (GHI) using machine learning.
2. Explain model predictions using SHAP.
3. Assess solar resource reliability.
4. Quantify prediction confidence.
5. Generate solar suitability recommendations.
6. Provide residential investment guidance.
7. Estimate system size, savings, and payback.
8. Deliver explainable recommendations.

---

# Dataset

Source: NASA POWER

Study Period:
2020–2024

Cities:

- Ahmedabad
- Bengaluru
- Bhopal
- Bhubaneswar
- Chandigarh
- Chennai
- Delhi
- Guwahati
- Hyderabad
- Jaipur
- Kochi
- Kolkata
- Mangalore
- Mumbai
- Pune

Target Variable:
Global Horizontal Irradiance (GHI)

---

# Machine Learning Framework

Model:
XGBoost Regressor

Input Features:

- Temperature
- Relative Humidity
- Cloud Cover
- Wind Speed
- Rainfall
- Previous Irradiance Features
- Seasonal Features

Evaluation Metrics:

- RMSE
- MAE
- MAPE
- R²

Explainability Method:
SHAP (SHapley Additive exPlanations)

---

# Solar Decision Support Framework (SDSF)

## Inputs

- Predicted GHI
- Historical GHI
- Reliability Score
- Prediction Confidence

## Outputs

- Mean Predicted GHI
- P10 GHI
- P50 GHI
- P90 GHI
- Reliability Score
- Prediction Confidence
- Solar Suitability
- Recommendation Explanation

## Purpose

To determine how suitable a city is for residential solar adoption while accounting for climatic consistency and prediction uncertainty.

---

# Residential Solar Investment Advisor (RSIA)

## Inputs

- City
- Monthly Electricity Bill
- Roof Area
- Budget
- SDSF Outputs

## Outputs

- Recommended System Size
- Annual Energy Generation
- Annual Savings
- Payback Period
- Lifetime Savings
- Net Benefit
- Investment Recommendation

## Purpose

To convert solar resource information into actionable investment guidance.

---

# Key Contributions

1. Explainable solar irradiance prediction using XGBoost and SHAP.
2. Solar Decision Support Framework (SDSF).
3. Reliability-aware solar suitability evaluation.
4. Residential Solar Investment Advisor (RSIA).
5. Explainable recommendation generation.
6. Integration of climate analytics and financial analysis.

---

# Research Workflow

Weather Data
↓
Feature Engineering
↓
XGBoost Prediction
↓
SHAP Explainability
↓
Reliability Assessment
↓
Prediction Confidence
↓
Solar Suitability
↓
Investment Analysis
↓
Final Recommendation

---

# Outputs Generated

NB11:
sdsf_city_dashboard.csv

NB12:
solar_investment_advisor_results.csv

---

# Limitations

- Limited to 15 Indian cities.
- Residential sector only.
- Based on historical NASA POWER data.
- No real installation validation.
- Economic assumptions may vary geographically.

---

# Future Scope

- Real-time weather integration.
- Rooftop image analysis.
- Live electricity tariff integration.
- Mobile application deployment.
- Expanded city coverage.
- Commercial and industrial solar analysis.
