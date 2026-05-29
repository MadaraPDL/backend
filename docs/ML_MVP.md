# PulseFi Real ML MVP - Usage Prediction

## Purpose

PulseFi includes a reproducible offline machine-learning MVP that predicts next-day internet usage in GB for a service line. This proves the project includes an implemented ML workflow, not only rules-based intelligence.

The current ML MVP is intentionally offline/demo-safe. It does not change deployed backend behavior, does not require production secrets, and does not connect to the live database.

## Current Scope

The ML MVP focuses on:

- generating PulseFi-style historical usage data,
- training a supervised usage prediction model,
- evaluating the model with MAE and RMSE,
- saving local model and metric artifacts,
- keeping existing rules-based backend intelligence as the runtime fallback.

## Dataset Source

The current dataset is generated demo data created by:

``powershell
python scripts/ml/generate_demo_usage_dataset.py
``

The generated data simulates PulseFi-style historical usage records for multiple service lines. It includes daily usage behavior, weekend effects, device count pressure, plan differences, rolling averages, trends, and occasional usage spikes.

The generated dataset is saved locally under:

``text
artifacts/ml/demo_usage_dataset.csv
``

Generated artifacts are gitignored and are not committed.

## Target

The prediction target is:

``text
target_next_day_usage_gb
``

This means the model learns to predict the next day's total usage in GB.

## Features

The model uses these input features:

- plan_monthly_limit_gb
- plan_speed_mbps
- device_count
- day_of_week
- is_weekend
- previous_day_usage_gb
- rolling_3_day_avg_gb
- rolling_7_day_avg_gb
- month_progress_ratio
- current_day_usage_gb

These features are practical for PulseFi because they reflect package size, package speed, connected-device pressure, calendar behavior, recent usage patterns, and current consumption.

## Model Choice

The current model is:

``text
normalized_linear_regression_gradient_descent
``

It is a supervised regression model trained from historical usage rows. Features are normalized, then the model learns weights using gradient descent.

This model was chosen because it is simple to explain in a university project report, deterministic, reproducible, safe to save as JSON, dependency-light, and understandable compared with a black-box model.

## Evaluation

The training script evaluates the model with:

- MAE: Mean Absolute Error
- RMSE: Root Mean Squared Error

MAE shows the average absolute prediction error in GB. RMSE penalizes larger errors more strongly.

The metrics are saved locally under:

``text
artifacts/ml/usage_prediction_metrics.json
``

The evaluation output is saved under:

``text
artifacts/ml/usage_prediction_evaluation.json
``

## Reproduction Commands

From the backend repository root:

``powershell
python scripts/ml/generate_demo_usage_dataset.py
python scripts/ml/train_usage_prediction_model.py
python scripts/ml/evaluate_usage_prediction_model.py
``

For local validation:

``powershell
python -m compileall app tests scripts
python -m pytest tests/ml
python -m pytest
git diff --check
``

When running the full test suite locally, use safe test environment overrides if local email delivery is enabled without Brevo test credentials:

``powershell
$env:DEBUG="true"
$env:EMAIL_DELIVERY_ENABLED="false"
$env:BREVO_API_KEY=""
python -m pytest
``

Do not paste or expose real production secrets.

## Saved Artifacts

The generated artifacts are local only:

``text
artifacts/ml/demo_usage_dataset.csv
artifacts/ml/usage_prediction_model.json
artifacts/ml/usage_prediction_metrics.json
artifacts/ml/usage_prediction_evaluation.json
``

These files are ignored by Git. Only artifacts/ml/.gitkeep is committed so the folder exists.

## How This Connects to PulseFi Intelligence

PulseFi already has backend intelligence that creates predictions, recommendations, and alerts through safe rules-based logic.

The Step 53A ML MVP adds a real offline ML pipeline that can support future prediction improvements. For now, deployed backend intelligence remains unchanged and rules-based logic remains the fallback.

A future safe integration could:

1. load a trained model only if an artifact exists,
2. validate the model artifact safely,
3. predict next-day or end-of-cycle usage,
4. fall back to existing rules-based intelligence if loading or prediction fails,
5. avoid breaking production startup.

## Limitations

The current ML MVP uses generated demo data, not real ISP production records. This is acceptable for the project MVP because it proves the complete ML workflow, but real-world accuracy would require real historical data.

The model is not yet deployed into backend runtime predictions. That is intentional to avoid destabilizing the deployed backend before final QA.

## Future Improvements

Future ML improvements can include:

- training on anonymized real PulseFi usage exports,
- predicting end-of-cycle usage,
- comparing linear regression, random forest, and gradient boosting models,
- tracking model versions,
- adding confidence bands,
- integrating the model behind a safe backend fallback,
- showing ML-backed prediction explanations in the mobile app.
