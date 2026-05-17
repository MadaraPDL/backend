from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from app.models.device import Device
from app.models.router import Router


@dataclass(frozen=True)
class RouterCapabilities:
    can_read_total_usage: bool
    can_read_connected_devices: bool
    can_read_device_usage: bool
    can_apply_bandwidth_limit: bool
    can_apply_device_priority: bool


@dataclass(frozen=True)
class RouterDeviceSnapshot:
    mac_address: str
    ip_address: str | None = None
    device_name: str | None = None
    device_type: str | None = None
    status: str = "connected"


@dataclass(frozen=True)
class RouterActionResult:
    success: bool
    action_type: str
    status: str
    message: str | None = None
    response_payload: dict | None = None
    error_message: str | None = None


class RouterAdapter(Protocol):
    adapter_name: str
    integration_mode: str
    is_simulator: bool

    def get_capabilities(self, router: Router) -> RouterCapabilities:
        """Return what this router adapter can safely support."""
        ...

    async def list_connected_devices(self, router: Router) -> list[RouterDeviceSnapshot]:
        """Return connected devices from the router or simulator."""
        ...

    async def apply_bandwidth_limit(
        self,
        *,
        router: Router,
        device: Device,
        limit_mbps: Decimal,
    ) -> RouterActionResult:
        """Apply a bandwidth limit to a device if supported."""
        ...

    async def apply_device_priority(
        self,
        *,
        router: Router,
        device: Device,
        priority_level: int,
    ) -> RouterActionResult:
        """Apply device priority if supported."""
        ...
