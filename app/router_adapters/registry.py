from __future__ import annotations

from app.models.router import Router
from app.router_adapters.base import RouterAdapter
from app.router_adapters.simulator import simulator_router_adapter


def get_router_adapter(router: Router) -> RouterAdapter:
    """
    Return the correct adapter for a router.

    For now, PulseFi uses the simulator adapter for every router.
    Later, this function can choose a real adapter based on router model,
    vendor, API endpoint, firmware, or stored capabilities.
    """
    return simulator_router_adapter
