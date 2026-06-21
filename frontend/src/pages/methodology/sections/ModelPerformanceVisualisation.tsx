/**
 * src/pages/methodology/sections/ModelPerformanceVisualisation.tsx
 * ─────────────────────────────────────────────────────────────────────────
 * Renders the actual research-pipeline figures generated in notebook
 * nb08 (XGBoost training/evaluation) rather than redrawing charts in
 * the frontend. Images are static artifacts copied verbatim from
 * outputs.zip — no chart libraries, no recomputation.
 * ─────────────────────────────────────────────────────────────────────────
 */

import { Section } from "@components/layout/Section";
import { Card } from "@components/ui/Card";
import { Eyebrow, DisplayLG, DisplaySM, Caption } from "@components/ui/Text";
import actualVsPredicted from "@assets/model/nb08_xgb_actual_vs_predicted.png";
import featureImportance from "@assets/model/nb08_xgb_feature_importance.png";
import learningCurve from "@assets/model/nb08_xgb_learning_curve.png";

interface Figure {
  src: string;
  alt: string;
  title: string;
  caption: string;
}

const FIGURES: Figure[] = [
  {
    src: actualVsPredicted,
    alt: "XGBoost actual vs predicted GHI scatter plot on the 2023–2024 test set",
    title: "Actual vs Predicted GHI",
    caption:
      "Test set (2023–2024). R² = 0.8831, RMSE = 0.4941 kWh/m²/day, MAPE = 9.71%. Points cluster tightly along the y = x line, indicating low prediction bias.",
  },
  {
    src: featureImportance,
    alt: "XGBoost feature importance bar chart",
    title: "Feature Importance",
    caption:
      "Gain-based importance ranking. 7-day GHI mean and prior-day GHI lag dominate, consistent with the SHAP global ranking below.",
  },
];

export function ModelPerformanceVisualisation() {
  return (
    <Section divider spacing="default">
      <div className="flex flex-col gap-8">
        <div className="flex flex-col gap-2 max-w-2xl">
          <Eyebrow>Model Performance Visualisation</Eyebrow>
          <DisplayLG>Evaluated on held-out 2023–2024 data</DisplayLG>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          {FIGURES.map((fig) => (
            <Card key={fig.title} padding="none" className="flex flex-col gap-0">
              <img src={fig.src} alt={fig.alt} className="w-full border-b border-ink" />
              <div className="flex flex-col gap-2 p-6">
                <DisplaySM as="h3" className="text-display-sm">
                  {fig.title}
                </DisplaySM>
                <Caption className="text-ink-300">{fig.caption}</Caption>
              </div>
            </Card>
          ))}
        </div>

        <Card padding="none" className="flex flex-col gap-0">
          <img
            src={learningCurve}
            alt="XGBoost training and validation learning curve"
            className="w-full border-b border-ink"
          />
          <div className="flex flex-col gap-2 p-6">
            <DisplaySM as="h3" className="text-display-sm">
              Learning Curve
            </DisplaySM>
            <Caption className="text-ink-300">
              Training vs validation error across boosting rounds, confirming the model
              converges without significant overfitting before early stopping.
            </Caption>
          </div>
        </Card>
      </div>
    </Section>
  );
}
