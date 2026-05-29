from __future__ import annotations

import argparse
import csv
import math
import random
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from app.ml.usage_features import DATASET_COLUMNS


DEFAULT_OUTPUT_PATH = ROOT_DIR / "artifacts" / "ml" / "demo_usage_dataset.csv"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate deterministic PulseFi-style demo usage data for ML training."
    )
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--seed", type=int, default=53)
    parser.add_argument("--service-lines", type=int, default=8)
    parser.add_argument("--days", type=int, default=120)
    args = parser.parse_args()

    output_path = Path(args.output)
    rows = generate_demo_usage_rows(
        seed=args.seed,
        service_line_count=args.service_lines,
        day_count=args.days,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=DATASET_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} demo ML rows at {output_path}")


def generate_demo_usage_rows(
    *,
    seed: int,
    service_line_count: int,
    day_count: int,
) -> list[dict[str, object]]:
    if service_line_count < 1:
        raise ValueError("service_line_count must be at least 1.")

    if day_count < 30:
        raise ValueError("day_count must be at least 30.")

    rng = random.Random(seed)
    start_date = date(2026, 1, 1)
    rows: list[dict[str, object]] = []

    for service_index in range(service_line_count):
        service_line_id = f"demo-service-line-{service_index + 1:02d}"
        plan_monthly_limit_gb = rng.choice([120, 180, 250, 350, 500])
        plan_speed_mbps = rng.choice([50, 100, 200, 300])
        device_count = rng.randint(3, 12)
        base_usage = plan_monthly_limit_gb / 30 * rng.uniform(0.45, 0.9)
        trend_per_day = rng.uniform(-0.01, 0.025)

        daily_usage_values = _build_daily_usage_series(
            rng=rng,
            day_count=day_count,
            service_index=service_index,
            base_usage=base_usage,
            trend_per_day=trend_per_day,
            device_count=device_count,
        )

        for day_offset in range(7, day_count - 1):
            current_date = start_date + timedelta(days=day_offset)
            current_usage = daily_usage_values[day_offset]
            previous_day_usage = daily_usage_values[day_offset - 1]
            rolling_3_day_avg = sum(daily_usage_values[day_offset - 3:day_offset]) / 3
            rolling_7_day_avg = sum(daily_usage_values[day_offset - 7:day_offset]) / 7
            target_next_day_usage = daily_usage_values[day_offset + 1]

            rows.append(
                {
                    "usage_date": current_date.isoformat(),
                    "service_line_id": service_line_id,
                    "plan_monthly_limit_gb": round(plan_monthly_limit_gb, 4),
                    "plan_speed_mbps": round(plan_speed_mbps, 4),
                    "device_count": round(device_count, 4),
                    "day_of_week": current_date.weekday(),
                    "is_weekend": 1 if current_date.weekday() >= 5 else 0,
                    "previous_day_usage_gb": round(previous_day_usage, 4),
                    "rolling_3_day_avg_gb": round(rolling_3_day_avg, 4),
                    "rolling_7_day_avg_gb": round(rolling_7_day_avg, 4),
                    "month_progress_ratio": round(((current_date.day - 1) / 30), 4),
                    "current_day_usage_gb": round(current_usage, 4),
                    "target_next_day_usage_gb": round(target_next_day_usage, 4),
                }
            )

    return rows


def _build_daily_usage_series(
    *,
    rng: random.Random,
    day_count: int,
    service_index: int,
    base_usage: float,
    trend_per_day: float,
    device_count: int,
) -> list[float]:
    values: list[float] = []

    for day_offset in range(day_count):
        day_of_week = day_offset % 7
        weekend_multiplier = 1.18 if day_of_week in {5, 6} else 1.0
        weekly_wave = 0.18 * math.sin((2 * math.pi * day_offset / 7) + service_index)
        long_cycle = 0.11 * math.sin((2 * math.pi * day_offset / 30) + service_index / 2)
        device_pressure = 1 + (device_count - 5) * 0.025
        trend_multiplier = 1 + (trend_per_day * day_offset)

        occasional_spike = 0.0
        if day_offset % (17 + service_index) == 0:
            occasional_spike = rng.uniform(0.15, 0.38)

        noise = rng.uniform(-0.12, 0.12)

        usage = base_usage
        usage *= weekend_multiplier
        usage *= device_pressure
        usage *= trend_multiplier
        usage *= 1 + weekly_wave + long_cycle + occasional_spike + noise

        values.append(round(max(0.25, usage), 4))

    return values


if __name__ == "__main__":
    main()
