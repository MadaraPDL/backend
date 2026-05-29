from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from app.ml.usage_features import (
    build_feature_matrix,
    load_usage_training_rows,
    split_time_ordered_rows,
    summarize_dataset,
)
from app.ml.usage_metrics import mean_absolute_error, root_mean_squared_error
from app.ml.usage_model import load_usage_model


DEFAULT_DATASET_PATH = ROOT_DIR / "artifacts" / "ml" / "demo_usage_dataset.csv"
DEFAULT_MODEL_PATH = ROOT_DIR / "artifacts" / "ml" / "usage_prediction_model.json"
DEFAULT_EVALUATION_PATH = ROOT_DIR / "artifacts" / "ml" / "usage_prediction_evaluation.json"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate a saved PulseFi usage prediction ML model."
    )
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET_PATH))
    parser.add_argument("--model", default=str(DEFAULT_MODEL_PATH))
    parser.add_argument("--output", default=str(DEFAULT_EVALUATION_PATH))
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    model_path = Path(args.model)

    if not dataset_path.exists():
        raise SystemExit(
            f"Dataset not found at {dataset_path}. "
            "Run scripts\\ml\\generate_demo_usage_dataset.py first."
        )

    if not model_path.exists():
        raise SystemExit(
            f"Model not found at {model_path}. "
            "Run scripts\\ml\\train_usage_prediction_model.py first."
        )

    rows = load_usage_training_rows(dataset_path)
    _, test_rows = split_time_ordered_rows(rows)

    test_features, test_targets = build_feature_matrix(test_rows)
    model = load_usage_model(model_path)
    predictions = model.predict_many(test_features)

    evaluation = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset_path": str(dataset_path),
        "model_path": str(model_path),
        "evaluated_rows": len(test_rows),
        "mae_gb": round(mean_absolute_error(test_targets, predictions), 4),
        "rmse_gb": round(root_mean_squared_error(test_targets, predictions), 4),
        "dataset_summary": summarize_dataset(rows),
        "sample_predictions": [
            {
                "usage_date": row.usage_date.isoformat(),
                "service_line_id": row.service_line_id,
                "actual_next_day_usage_gb": round(actual, 4),
                "predicted_next_day_usage_gb": round(predicted, 4),
                "absolute_error_gb": round(abs(actual - predicted), 4),
            }
            for row, actual, predicted in list(zip(test_rows, test_targets, predictions, strict=True))[:10]
        ],
    }

    _write_json(evaluation, args.output)

    print(json.dumps(evaluation, indent=2, sort_keys=True))


def _write_json(payload: dict[str, object], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
