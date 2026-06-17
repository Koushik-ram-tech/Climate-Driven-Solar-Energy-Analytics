# Methodology Notes

## NB11 — Solar Decision Support Framework

### Reliability Score

Purpose:
Measure long-term solar resource consistency.

Interpretation:

* High RS → stable solar resource
* Medium RS → seasonal variation
* Low RS → higher uncertainty

Categories:

* Consistent Producer
* Seasonal Producer
* Variable Producer

---

### Prediction Confidence

Based on city-level forecasting performance.

Thresholds:

MAPE ≤ 25%
→ High

25% < MAPE ≤ 35%
→ Medium

MAPE > 35%
→ Low

---

### GHI Potential Classification

Mean Predicted GHI

≥ 5.5
→ Excellent

4.5–5.5
→ Good

3.5–4.5
→ Moderate

< 3.5
→ Poor

---

### Suitability Framework

Base suitability determined by GHI bracket.

Adjustments:

Upgrade:
RS ≥ 75 and Confidence = High

Downgrade:
Confidence = Low

Final Tiers:

* Highly Suitable
* Suitable
* Moderately Suitable
* Less Suitable

---

## NB12 — Residential Solar Investment Advisor

### Consumption Estimation

Monthly Bill
↓
Annual Consumption

---

### System Sizing

Uses:

* Electricity Consumption
* Roof Area
* Budget
* Local Solar Resource

Outputs:

* Minimum System Size
* Recommended System Size
* Maximum Feasible System Size

---

### Annual Generation

Based on:

Annual Generation =
System Size × Mean GHI × 365 × Performance Ratio

---

### Annual Savings

Annual Savings =
Annual Generation × Electricity Tariff

---

### Payback Period

Payback =
Net System Cost ÷ Annual Savings

---

### Lifetime Savings

Lifetime:
25 Years

Includes:

* Tariff Escalation
* Panel Degradation

---

### Recommendation Categories

* Highly Recommended
* Recommended
* Consider Carefully
* Not Recommended

Based on:

* Suitability
* Payback
* Investment Feasibility

---

## SHAP Findings

Most Influential Feature:

Cloud Cover

Other Important Drivers:

* Temperature
* Humidity
* Seasonal Conditions
* Previous Irradiance

Conclusion:

Cloud Cover consistently exhibited the strongest impact on solar irradiance prediction across study cities.
