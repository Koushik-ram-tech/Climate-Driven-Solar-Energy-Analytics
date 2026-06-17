# BACKEND_ARCHITECTURE

# AI-Powered Residential Solar Investment Advisor Using Explainable Machine Learning

## Backend Architecture Specification

Version: 1.0

Status: Final Architecture Design

---

# 1. Purpose

This document defines the backend architecture for deploying the research frameworks developed in this project:

1. Solar Decision Support Framework (SDSF)
2. Residential Solar Investment Advisor (RSIA)

The backend exposes the outputs of these frameworks through REST APIs that can be consumed by a React frontend.

The backend is not responsible for training machine learning models.

The backend serves pre-computed framework outputs and performs lightweight advisory calculations.

---

# 2. System Architecture

```text
                    React Frontend
                           │
                           ▼
                    FastAPI Backend
                           │
      ┌────────────────────┼────────────────────┐
      │                    │                    │
      ▼                    ▼                    ▼
 Readiness Service   Advisor Service   Explanation Service
      │                    │                    │
      └────────────────────┼────────────────────┘
                           │
                           ▼
                    CSV Data Layer
                           │
      ┌────────────────────┼────────────────────┐
      │                    │                    │
      ▼                    ▼                    ▼
sdsf_city_dashboard   advisor_results    SHAP outputs
```

---

# 3. Design Principles

## Principle 1 — Research First

The research notebooks remain the source of truth.

The backend must never modify:

- SDSF methodology
- Reliability Score
- Prediction Confidence
- Suitability Framework
- Investment Recommendation Logic

All research logic is frozen.

---

## Principle 2 — No Model Retraining

The web application should never retrain XGBoost models.

Model training remains offline inside notebooks.

Benefits:

- Faster responses
- Lower hosting costs
- Simpler deployment
- Easier maintenance

---

## Principle 3 — Lightweight Architecture

Project Scope:

- 15 Cities
- Static Framework Outputs
- No Authentication
- No User Accounts
- No Payments

Therefore:

No PostgreSQL

No Redis

No Kafka

No Celery

No Kubernetes

No Microservices

CSV-based storage is sufficient.

---

# 4. Technology Stack

## Frontend

React

Tailwind CSS

Framer Motion

Vercel Deployment

---

## Backend

FastAPI

Pydantic

Pandas

Uvicorn

Render Deployment

---

## Data Storage

CSV Files

No database required.

---

# 5. Directory Structure

```text
backend/

├── app/
│
├── api/
│   ├── cities.py
│   ├── readiness.py
│   ├── advisor.py
│   ├── explanations.py
│   └── methodology.py
│
├── services/
│   ├── readiness_service.py
│   ├── advisor_service.py
│   └── explanation_service.py
│
├── schemas/
│   ├── advisor_request.py
│   ├── advisor_response.py
│   ├── readiness_response.py
│   └── explanation_response.py
│
├── data/
│   ├── sdsf_city_dashboard.csv
│   ├── solar_investment_advisor_results.csv
│   └── shap_summary.csv
│
├── utils/
│   ├── calculations.py
│   └── validation.py
│
├── tests/
│
├── main.py
│
└── requirements.txt
```

---

# 6. Data Sources

## SDSF Dashboard

File:

```text
sdsf_city_dashboard.csv
```

Contains:

- City
- Mean GHI
- P10
- P50
- P90
- Reliability Score
- Reliability Category
- Prediction Confidence
- Suitability
- Recommendation Explanation

Purpose:

Solar Readiness Framework outputs.

---

## Investment Advisor Results

File:

```text
solar_investment_advisor_results.csv
```

Contains:

- System Size
- Annual Generation
- Annual Savings
- Payback Period
- Lifetime Savings
- Net Benefit
- Investment Recommendation

Purpose:

Investment analysis outputs.

---

## SHAP Outputs

Contains:

- Feature Importance
- SHAP Rankings
- Explanation Narratives

Purpose:

Explainable AI layer.

---

# 7. Services

## 7.1 Readiness Service

Purpose:

Provide Solar Readiness Framework outputs.

Methods:

```python
get_city_readiness(city)
```

Returns:

- Mean GHI
- Reliability Score
- Confidence
- Suitability
- Explanation

---

## 7.2 Advisor Service

Purpose:

Generate personalized investment recommendations.

Inputs:

- City
- Monthly Bill
- Roof Area
- Budget

Outputs:

- Recommended System Size
- Annual Generation
- Annual Savings
- Payback
- Lifetime Savings
- Recommendation

---

## 7.3 Explanation Service

Purpose:

Provide explainable AI insights.

Returns:

- Top influencing features
- SHAP explanation
- Plain-language interpretation

Example:

"Cloud cover is the strongest driver of solar irradiance prediction in Bengaluru."

---

# 8. API Endpoints

---

## Health Check

```http
GET /health
```

Response:

```json
{
  "status": "healthy"
}
```

---

## Cities

```http
GET /cities
```

Purpose:

Return supported cities.

Response:

```json
["Ahmedabad", "Bengaluru", "Chennai"]
```

---

## Solar Readiness

```http
GET /readiness/{city}
```

Purpose:

Return SDSF outputs for a city.

Response:

```json
{
  "city": "Bengaluru",
  "mean_ghi": 5.27,
  "reliability_score": 81.1,
  "confidence": "High",
  "suitability": "Highly Suitable"
}
```

---

## Investment Advisor

```http
POST /advisor
```

Request:

```json
{
  "city": "Bengaluru",
  "monthly_bill": 3000,
  "roof_area": 500,
  "budget": 400000
}
```

Response:

```json
{
  "system_size": 3,
  "annual_generation": 4503,
  "annual_savings": 31520,
  "payback_years": 3.7,
  "lifetime_savings": 1224051,
  "recommendation": "Highly Recommended"
}
```

---

## AI Explanations

```http
GET /explanations/{city}
```

Purpose:

Return city-specific explainability information.

Response:

```json
{
  "top_factor": "Cloud Cover",
  "message": "Cloud cover is the strongest factor affecting solar irradiance in this city."
}
```

---

## Framework Methodology

```http
GET /methodology
```

Purpose:

Provide methodology information for the About page.

---

# 9. Request Validation

Validation Library:

Pydantic

---

## Monthly Bill

Minimum:

₹500

Maximum:

₹100000

---

## Roof Area

Minimum:

50 sq ft

Maximum:

5000 sq ft

---

## Budget

Minimum:

₹50000

Maximum:

₹5000000

---

## City

Must exist in supported city list.

---

# 10. Error Handling

## Invalid City

HTTP 404

Example:

```json
{
  "error": "City not supported"
}
```

---

## Validation Error

HTTP 422

Example:

```json
{
  "error": "Invalid roof area"
}
```

---

## Internal Server Error

HTTP 500

Example:

```json
{
  "error": "Unexpected server error"
}
```

---

# 11. Security

## CORS

Allow requests only from frontend domain.

---

## Environment Variables

Store:

```text
APP_ENV
API_URL
SECRET_KEY
```

---

## Input Sanitization

Validate:

- Strings
- Numeric ranges
- Supported city names

before processing.

---

# 12. Performance Strategy

All CSV files are loaded once during startup.

Data is cached in memory.

Benefits:

- Fast API responses
- Reduced disk access
- Lower server load

Expected response time:

< 100 ms

---

# 13. Testing Strategy

## Unit Tests

Test:

- Consumption estimation
- System sizing
- Savings calculations
- Payback calculations

---

## Integration Tests

Test:

- API responses
- Endpoint availability
- JSON structures

---

## Validation Tests

Test:

- Invalid city
- Invalid budget
- Invalid roof area

---

# 14. Deployment Architecture

## Frontend

Platform:

Vercel

Responsibilities:

- User Interface
- Dashboard
- Forms
- Visualizations

---

## Backend

Platform:

Render

Responsibilities:

- API Layer
- Calculations
- Data Serving

---

## Data Layer

CSV files bundled with backend.

No external database required.

---

# 15. Dissertation Contribution Mapping

Research Layer

↓

XGBoost Prediction

↓

SHAP Explainability

↓

Solar Decision Support Framework (SDSF)

↓

Residential Solar Investment Advisor (RSIA)

↓

FastAPI Backend

↓

React Frontend

↓

End User

The backend acts as an operational layer that exposes the research outputs without altering the underlying methodology.

---

# 16. Future Enhancements

Version 2:

- Additional Indian cities
- Dynamic tariff database
- Real-time weather updates

Version 3:

- Rooftop image analysis
- Automated solar sizing
- User accounts
- Cloud database integration

Version 4:

- Nationwide deployment
- Mobile application
- Utility-scale solar assessment

```

```
