from __future__ import annotations

import csv
from pathlib import Path

from app.ml.usage_features import (
    DATASET_COLUMNS,
    FEATURE_COLUMNS,
    build_feature_matrix,
    load_usage_training_rows,
    split_time_ordered_rows,
)
from app.ml.usage_metrics import mean_absolute_error, root_mean_squared_error
from app.ml.usage_model import load_usage_model, save_usage_model, train_usage_regression_model


def test_usage_training_rows_load_expected_columns(tmp_path: Path) -> None:
    dataset_path = tmp_path / "usage.csv"

    with dataset_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=DATASET_COLUMNS)
        writer.writeheader()

        for index in range(12):
            writer.writerow(
                {
                    "usage_date": f"2026-01-{index + 1:02d}",
                    "service_line_id": "demo-service-line-01",
                    "plan_monthly_limit_gb": 250,
                    "plan_speed_mbps": 100,
                    "device_count": 6,
                    "day_of_week": index % 7,
                    "is_weekend": 1 if index % 7 in {5, 6} else 0,
                    "previous_day_usage_gb": 5 + index,
                    "rolling_3_day_avg_gb": 5.5 + index,
                    "rolling_7_day_avg_gb": 6.0 + index,
                    "month_progress_ratio": index / 30,
                    "current_day_usage_gb": 6 + index,
                    "target_next_day_usage_gb": 7 + index,
                }
            )

    rows = load_usage_training_rows(dataset_path)
    features, targets = build_feature_matrix(rows)

    assert len(rows) == 12
    assert len(features[0]) == len(FEATURE_COLUMNS)
    assert targets[0] == 7


def test_time_ordered_split_keeps_training_before_test(tmp_path: Path) -> None:
    dataset_path = tmp_path / "usage.csv"

    with dataset_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=DATASET_COLUMNS)
        writer.writeheader()

        for index in range(20):
            writer.writerow(
                {
                    "usage_date": f"2026-01-{index + 1:02d}",
                    "service_line_id": "demo-service-line-01",
                    "plan_monthly_limit_gb": 180,
                    "plan_speed_mbps": 50,
                    "device_count": 4,
                    "day_of_week": index % 7,
                    "is_weekend": 1 if index % 7 in {5, 6} else 0,
                    "previous_day_usage_gb": index,
                    "rolling_3_day_avg_gb": index,
                    "rolling_7_day_avg_gb": index,
                    "month_progress_ratio": index / 30,
                    "current_day_usage_gb": index,
                    "target_next_day_usage_gb": index + 1,
                }
            )

    rows = load_usage_training_rows(dataset_path)
    train_rows, test_rows = split_time_ordered_rows(rows, test_ratio=0.25)

    assert len(train_rows) == 15
    assert len(test_rows) == 5
    assert max(row.usage_date for row in train_rows) < min(row.usage_date for row in test_rows)


def test_usage_regression_model_trains_predicts_and_round_trips(tmp_path: Path) -> None:
    feature_columns = ["current_day_usage_gb", "rolling_3_day_avg_gb"]
    features = [[float(index), float(index) + 0.5] for index in range(1, 25)]
    targets = [(2 * row[0]) + 1 for row in features]

    model = train_usage_regression_model(
        features,
        targets,
        feature_columns=feature_columns,
        epochs=1200,
        learning_rate=0.04,
        l2_penalty=0.0,
    )

    predictions = model.predict_many(features)
    mae = mean_absolute_error(targets, predictions)
    rmse = root_mean_squared_error(targets, predictions)

    assert mae < 0.25
    assert rmse < 0.3

    model_path = tmp_path / "model.json"
    save_usage_model(model, model_path)
    loaded_model = load_usage_model(model_path)

    assert loaded_model.feature_columns == feature_columns
    assert loaded_model.predict_one([10.0, 10.5]) > 0
