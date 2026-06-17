# FRONTEND_ARCHITECTURE

# AI-Powered Residential Solar Investment Advisor

## Frontend Architecture Specification

Version: 1.0

Status: Final Frontend Design

---

# 1. Purpose

The frontend serves as the user-facing layer of the project.

Its responsibilities are:

- Collect user inputs
- Display Solar Readiness results
- Display Investment Advisor results
- Visualize AI explanations
- Present research outputs in an intuitive manner

The frontend should feel:

- Modern
- Premium
- Intelligent
- Trustworthy
- Fast
- Explainable

---

# 2. Application Structure

Home
│
├── Assessment
│
├── Results Dashboard
│
├── Solar Readiness Explorer
│
├── Explainable AI
│
└── About Framework

---

# 3. Page Architecture

## Home Page

Purpose:

Introduce the platform and communicate value.

Primary Message:

"Find out whether solar is a smart investment for your home."

Sections:

1. Hero Section
2. Key Benefits
3. City Highlights
4. How It Works
5. Call To Action

---

## Assessment Page

Purpose:

Collect user information.

Inputs:

- City
- Monthly Electricity Bill
- Roof Area
- Budget

Output:

Submit to Advisor API

POST /advisor

---

## Results Dashboard

Purpose:

Display personalized results.

This is the most important page.

---

# 4. Results Dashboard Layout

Top Section

Recommendation Banner

Examples:

Highly Recommended

Recommended

Consider Carefully

Not Recommended

---

Primary Metrics

Displayed Above Fold

1. Payback Period

2. Annual Savings

3. Recommended System Size

4. Lifetime Savings

These should be the first things users see.

---

Secondary Metrics

Solar Readiness

- Mean GHI
- Reliability Score
- Confidence
- Suitability

---

# 5. Dashboard Tabs

## Tab 1

Investment Analysis

Contains:

- System Size
- Annual Generation
- Annual Savings
- Payback
- Lifetime Savings
- Net Benefit

---

## Tab 2

Solar Readiness

Contains:

- Mean GHI
- P10
- P50
- P90
- Reliability Score
- Confidence
- Suitability

---

## Tab 3

AI Explanation

Contains:

- Top SHAP Factors
- Cloud Cover Insights
- Feature Importance
- Explanation Narrative

---

# 6. Solar Readiness Explorer

Purpose:

Compare cities.

Data Source:

GET /readiness/{city}

Displays:

- Mean GHI
- Reliability
- Confidence
- Suitability

Supported Cities:

Ahmedabad

Bengaluru

Bhopal

Bhubaneswar

Chandigarh

Chennai

Delhi

Guwahati

Hyderabad

Jaipur

Kochi

Kolkata

Mangalore

Mumbai

Pune

---

# 7. Explainable AI Page

Purpose:

Show how predictions are made.

Sections:

1. SHAP Overview

2. Top Features

3. Cloud Cover Impact

4. City-Level Explanations

Primary Message:

"Cloud cover is the strongest factor affecting solar irradiance predictions."

---

# 8. About Framework Page

Purpose:

Explain research methodology.

Sections:

Project Overview

Dataset

XGBoost Model

SHAP Explainability

Solar Decision Support Framework

Residential Solar Investment Advisor

Limitations

Future Work

---

# 9. Component Hierarchy

App

├── Navbar

├── Hero

├── AssessmentForm

├── RecommendationBanner

├── MetricCard

├── ReadinessCard

├── SuitabilityCard

├── ReliabilityCard

├── ConfidenceCard

├── SavingsCard

├── PaybackCard

├── SystemSizeCard

├── LifetimeSavingsCard

├── AIExplanationCard

├── CityComparisonTable

└── Footer

---

# 10. API Integration

GET /cities

Used For:

City Dropdown

---

GET /readiness/{city}

Used For:

City Explorer

Solar Readiness Tab

---

POST /advisor

Used For:

Assessment Form

Results Dashboard

---

GET /explanations/{city}

Used For:

AI Explanation Page

---

GET /methodology

Used For:

About Framework Page

---

# 11. State Management

Local State:

Form Inputs

Loading States

Error States

---

Global State:

Current Assessment Result

Selected City

Framework Metadata

---

# 12. Error Handling

Invalid Inputs

Display inline validation.

---

API Failure

Display:

"Unable to retrieve results. Please try again."

---

No Results

Display fallback message.

---

# 13. Responsive Design

Desktop

Full Dashboard Layout

---

Tablet

2-column Grid

---

Mobile

Single Column Layout

Sticky Recommendation Banner

Collapsible Sections

---

# 14. Animation Strategy

Library:

Framer Motion

Animations:

Page Fade-In

Card Entrance

Hover Lift

Number Count-Up

Smooth Tab Switching

Focus:

Premium UX

Avoid excessive animations.

---

# 15. Accessibility

Requirements:

WCAG AA

Keyboard Navigation

Screen Reader Support

Sufficient Color Contrast

Accessible Forms

Accessible Charts

---

# 16. Implementation Order

Phase 1

Project Setup

API Integration

---

Phase 2

Assessment Page

Results Dashboard

---

Phase 3

Solar Readiness Explorer

AI Explanation Page

---

Phase 4

About Framework

Responsive Design

Animations

---

Phase 5

Testing

Deployment

---

# 17. Success Criteria

A user should be able to:

1. Select a city

2. Enter:
   - Monthly Bill
   - Roof Area
   - Budget

3. Receive:
   - Solar Readiness Assessment
   - Investment Recommendation
   - Payback Estimate
   - Savings Estimate
   - AI Explanation

within a few seconds.

The frontend should communicate research outputs clearly while maintaining a modern and professional user experience.