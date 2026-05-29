from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class UsageRegressionModel:
    """A small JSON-serializable regression model for PulseFi usage prediction.

    This is real supervised ML: the model learns weights from historical usage
    rows by minimizing prediction error with gradient descent.
    """

    feature_columns: list[str]
    feature_means: list[float]
    feature_scales: list[float]
    weights: list[float]
    bias: float

    def predict_one(self, features: list[float]) -> float:
        if len(features) != len(self.feature_columns):
            raise ValueError(
                f"Expected {len(self.feature_columns)} features, got {len(features)}."
            )

        scaled_features = [
            (value - mean) / scale
            for value, mean, scale in zip(
                features,
                self.feature_means,
                self.feature_scales,
                strict=True,
            )
        ]

        prediction = self.bias + sum(
            weight * value
            for weight, value in zip(self.weights, scaled_features, strict=True)
        )

        return max(0.0, prediction)

    def predict_many(self, feature_matrix: list[list[float]]) -> list[float]:
        return [self.predict_one(features) for features in feature_matrix]


def train_usage_regression_model(
    feature_matrix: list[list[float]],
    targets: list[float],
    *,
    feature_columns: list[str],
    epochs: int = 1800,
    learning_rate: float = 0.035,
    l2_penalty: float = 0.001,
) -> UsageRegressionModel:
    """Train a normalized linear regression model with gradient descent."""

    _validate_training_input(feature_matrix, targets, feature_columns)

    row_count = len(feature_matrix)
    feature_count = len(feature_columns)

    feature_means = _column_means(feature_matrix)
    feature_scales = _column_scales(feature_matrix, feature_means)

    scaled_matrix = [
        [
            (value - feature_means[index]) / feature_scales[index]
            for index, value in enumerate(row)
        ]
        for row in feature_matrix
    ]

    weights = [0.0 for _ in range(feature_count)]
    bias = sum(targets) / len(targets)

    for _ in range(epochs):
        weight_gradients = [0.0 for _ in range(feature_count)]
        bias_gradient = 0.0

        for features, target in zip(scaled_matrix, targets, strict=True):
            prediction = bias + sum(
                weight * value
                for weight, value in zip(weights, features, strict=True)
            )
            error = prediction - target

            bias_gradient += error

            for feature_index, feature_value in enumerate(features):
                weight_gradients[feature_index] += error * feature_value

        bias -= learning_rate * (2 * bias_gradient / row_count)

        for feature_index in range(feature_count):
            regularization = 2 * l2_penalty * weights[feature_index]
            gradient = (2 * weight_gradients[feature_index] / row_count) + regularization
            weights[feature_index] -= learning_rate * gradient

    return UsageRegressionModel(
        feature_columns=feature_columns,
        feature_means=feature_means,
        feature_scales=feature_scales,
        weights=weights,
        bias=bias,
    )


def save_usage_model(model: UsageRegressionModel, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(asdict(model), file, indent=2, sort_keys=True)


def load_usage_model(path: str | Path) -> UsageRegressionModel:
    model_path = Path(path)

    with model_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    return UsageRegressionModel(
        feature_columns=list(payload["feature_columns"]),
        feature_means=[float(value) for value in payload["feature_means"]],
        feature_scales=[float(value) for value in payload["feature_scales"]],
        weights=[float(value) for value in payload["weights"]],
        bias=float(payload["bias"]),
    )


def _validate_training_input(
    feature_matrix: list[list[float]],
    targets: list[float],
    feature_columns: list[str],
) -> None:
    if not feature_matrix:
        raise ValueError("feature_matrix cannot be empty.")

    if len(feature_matrix) != len(targets):
        raise ValueError("feature_matrix and targets must have the same length.")

    if not feature_columns:
        raise ValueError("feature_columns cannot be empty.")

    expected_feature_count = len(feature_columns)

    for row in feature_matrix:
        if len(row) != expected_feature_count:
            raise ValueError(
                f"Each feature row must contain {expected_feature_count} values."
            )


def _column_means(feature_matrix: list[list[float]]) -> list[float]:
    row_count = len(feature_matrix)
    feature_count = len(feature_matrix[0])

    return [
        sum(row[feature_index] for row in feature_matrix) / row_count
        for feature_index in range(feature_count)
    ]


def _column_scales(feature_matrix: list[list[float]], means: list[float]) -> list[float]:
    row_count = len(feature_matrix)
    feature_count = len(feature_matrix[0])
    scales: list[float] = []

    for feature_index in range(feature_count):
        variance = sum(
            (row[feature_index] - means[feature_index]) ** 2
            for row in feature_matrix
        ) / row_count
        scale = variance ** 0.5
        scales.append(scale if scale > 0 else 1.0)

    return scales
