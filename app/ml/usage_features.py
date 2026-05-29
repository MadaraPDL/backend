from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


FEATURE_COLUMNS: list[str] = [
    "plan_monthly_limit_gb",
    "plan_speed_mbps",
    "device_count",
    "day_of_week",
    "is_weekend",
    "previous_day_usage_gb",
    "rolling_3_day_avg_gb",
    "rolling_7_day_avg_gb",
    "month_progress_ratio",
    "current_day_usage_gb",
]

DATASET_COLUMNS: list[str] = [
    "usage_date",
    "service_line_id",
    *FEATURE_COLUMNS,
    "target_next_day_usage_gb",
]


@dataclass(frozen=True)
class UsageTrainingRow:
    """One supervised ML row for next-day usage prediction."""

    usage_date: date
    service_line_id: str
    features: list[float]
    target_next_day_usage_gb: float


def load_usage_training_rows(path: str | Path) -> list[UsageTrainingRow]:
    """Load PulseFi-style usage rows from CSV.

    The target is the next day's total usage in GB.
    """

    dataset_path = Path(path)

    with dataset_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        missing_columns = [column for column in DATASET_COLUMNS if column not in (reader.fieldnames or [])]

        if missing_columns:
            joined = ", ".join(missing_columns)
            raise ValueError(f"Dataset is missing required columns: {joined}")

        rows = [_parse_training_row(raw_row) for raw_row in reader]

    return sorted(rows, key=lambda row: (row.usage_date, row.service_line_id))


def build_feature_matrix(rows: Iterable[UsageTrainingRow]) -> tuple[list[list[float]], list[float]]:
    """Return model features and target values from parsed training rows."""

    feature_matrix: list[list[float]] = []
    targets: list[float] = []

    for row in rows:
        feature_matrix.append(row.features)
        targets.append(row.target_next_day_usage_gb)

    if not feature_matrix:
        raise ValueError("Cannot build a feature matrix from an empty dataset.")

    return feature_matrix, targets


def split_time_ordered_rows(
    rows: list[UsageTrainingRow],
    *,
    test_ratio: float = 0.2,
) -> tuple[list[UsageTrainingRow], list[UsageTrainingRow]]:
    """Split rows in time order to avoid random future-to-past leakage."""

    if not 0 < test_ratio < 1:
        raise ValueError("test_ratio must be between 0 and 1.")

    if len(rows) < 10:
        raise ValueError("At least 10 rows are required for a train/test split.")

    split_index = int(len(rows) * (1 - test_ratio))
    split_index = max(1, min(split_index, len(rows) - 1))

    return rows[:split_index], rows[split_index:]


def summarize_dataset(rows: list[UsageTrainingRow]) -> dict[str, object]:
    """Return a small, report-friendly dataset summary."""

    if not rows:
        raise ValueError("Cannot summarize an empty dataset.")

    service_line_ids = {row.service_line_id for row in rows}
    targets = [row.target_next_day_usage_gb for row in rows]

    return {
        "row_count": len(rows),
        "service_line_count": len(service_line_ids),
        "start_date": min(row.usage_date for row in rows).isoformat(),
        "end_date": max(row.usage_date for row in rows).isoformat(),
        "target_min_gb": round(min(targets), 4),
        "target_max_gb": round(max(targets), 4),
        "target_avg_gb": round(sum(targets) / len(targets), 4),
        "feature_columns": FEATURE_COLUMNS,
    }


def _parse_training_row(raw_row: dict[str, str]) -> UsageTrainingRow:
    return UsageTrainingRow(
        usage_date=date.fromisoformat(raw_row["usage_date"]),
        service_line_id=raw_row["service_line_id"],
        features=[_to_float(raw_row, column) for column in FEATURE_COLUMNS],
        target_next_day_usage_gb=_to_float(raw_row, "target_next_day_usage_gb"),
    )


def _to_float(raw_row: dict[str, str], column: str) -> float:
    value = raw_row[column]

    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"Column {column!r} must be numeric, got {value!r}.") from exc
