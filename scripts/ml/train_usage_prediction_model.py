from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from app.ml.usage_features import (
    FEATURE_COLUMNS,
    build_feature_matrix,
    load_usage_training_rows,
    split_time_ordered_rows,
    summarize_dataset,
)
from app.ml.usage_metrics import mean_absolute_error, root_mean_squared_error
from app.ml.usage_model import save_usage_model, train_usage_regression_model


DEFAULT_DATASET_PATH = ROOT_DIR / "artifacts" / "ml" / "demo_usage_dataset.csv"
DEFAULT_MODEL_PATH = ROOT_DIR / "artifacts" / "ml" / "usage_prediction_model.json"
DEFAULT_METRICS_PATH = ROOT_DIR / "artifacts" / "ml" / "usage_prediction_metrics.json"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train the PulseFi next-day usage prediction ML model."
    )
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET_PATH))
    parser.add_argument("--model-output", default=str(DEFAULT_MODEL_PATH))
    parser.add_argument("--metrics-output", default=str(DEFAULT_METRICS_PATH))
    args = parser.parse_args()

    dataset_path = Path(args.dataset)

    if not dataset_path.exists():
        raise SystemExit(
            f"Dataset not found at {dataset_path}. "
            "Run scripts\\ml\\generate_demo_usage_dataset.py first."
        )

    rows = load_usage_training_rows(dataset_path)
    train_rows, test_rows = split_time_ordered_rows(rows)

    train_features, train_targets = build_feature_matrix(train_rows)
    test_features, test_targets = build_feature_matrix(test_rows)

    model = train_usage_regression_model(
        train_features,
        train_targets,
        feature_columns=FEATURE_COLUMNS,
    )

    predictions = model.predict_many(test_features)

    metrics = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset_path": str(dataset_path),
        "model_path": str(Path(args.model_output)),
        "model_type": "normalized_linear_regression_gradient_descent",
        "target": "target_next_day_usage_gb",
        "train_rows": len(train_rows),
        "test_rows": len(test_rows),
        "mae_gb": round(mean_absolute_error(test_targets, predictions), 4),
        "rmse_gb": round(root_mean_squared_error(test_targets, predictions), 4),
        "dataset_summary": summarize_dataset(rows),
        "limitations": [
            "This Step 53A dataset is generated demo data, not real ISP production data.",
            "The model is an offline MVP and is not wired into deployed intelligence endpoints yet.",
            "Existing rules-based intelligence remains the runtime fallback.",
        ],
    }

    save_usage_model(model, args.model_output)
    _write_json(metrics, args.metrics_output)

    print(json.dumps(metrics, indent=2, sort_keys=True))


def _write_json(payload: dict[str, object], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
