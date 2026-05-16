from app.router_adapters.base import (
    RouterActionResult,
    RouterAdapter,
    RouterCapabilities,
    RouterDeviceSnapshot,
)
from app.router_adapters.registry import get_router_adapter
from app.router_adapters.simulator import SimulatorRouterAdapter

__all__ = [
    "RouterActionResult",
    "RouterAdapter",
    "RouterCapabilities",
    "RouterDeviceSnapshot",
    "SimulatorRouterAdapter",
    "get_router_adapter",
]
