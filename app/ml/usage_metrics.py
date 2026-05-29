from __future__ import annotations

import math


def mean_absolute_error(actual_values: list[float], predicted_values: list[float]) -> float:
    """Return MAE, the average absolute prediction error."""

    _validate_metric_inputs(actual_values, predicted_values)

    total_error = sum(
        abs(actual - predicted)
        for actual, predicted in zip(actual_values, predicted_values, strict=True)
    )

    return total_error / len(actual_values)


def root_mean_squared_error(actual_values: list[float], predicted_values: list[float]) -> float:
    """Return RMSE, which penalizes larger prediction errors more strongly."""

    _validate_metric_inputs(actual_values, predicted_values)

    mean_squared_error = sum(
        (actual - predicted) ** 2
        for actual, predicted in zip(actual_values, predicted_values, strict=True)
    ) / len(actual_values)

    return math.sqrt(mean_squared_error)


def _validate_metric_inputs(actual_values: list[float], predicted_values: list[float]) -> None:
    if not actual_values:
        raise ValueError("Metric inputs cannot be empty.")

    if len(actual_values) != len(predicted_values):
        raise ValueError("Actual and predicted values must have the same length.")
