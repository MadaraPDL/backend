from __future__ import annotations

from typing import Literal


SimulatorScenario = Literal[
    "normal_usage",
    "high_usage",
    "near_plan_limit",
    "exceeded_plan",
    "new_device",
    "policy_failure",
    "heavy_device_usage",
]

DEFAULT_SIMULATOR_SCENARIO: SimulatorScenario = "normal_usage"

SIMULATOR_SCENARIOS: tuple[SimulatorScenario, ...] = (
    "normal_usage",
    "high_usage",
    "near_plan_limit",
    "exceeded_plan",
    "new_device",
    "policy_failure",
    "heavy_device_usage",
)

