from __future__ import annotations

from decimal import Decimal

from app.models.device import Device
from app.models.router import Router
from app.router_adapters.base import (
    RouterActionResult,
    RouterAdapter,
    RouterCapabilities,
    RouterDeviceSnapshot,
)


class SimulatorRouterAdapter:
    adapter_name = "simulator"
    integration_mode = "simulator"
    is_simulator = True

    def get_capabilities(self, router: Router) -> RouterCapabilities:
        return RouterCapabilities(
            can_read_total_usage=True,
            can_read_connected_devices=True,
            can_read_device_usage=True,
            can_apply_bandwidth_limit=True,
            can_apply_device_priority=True,
        )

    async def list_connected_devices(self, router: Router) -> list[RouterDeviceSnapshot]:
        router_label = router.router_name or "PulseFi Demo Router"

        return [
            RouterDeviceSnapshot(
                mac_address="AA:BB:CC:DD:EE:01",
                ip_address="192.168.1.10",
                device_name=f"{router_label} Demo Phone",
                device_type="phone",
                status="connected",
            ),
            RouterDeviceSnapshot(
                mac_address="AA:BB:CC:DD:EE:02",
                ip_address="192.168.1.20",
                device_name=f"{router_label} Demo Laptop",
                device_type="laptop",
                status="connected",
            ),
        ]

    async def apply_bandwidth_limit(
        self,
        *,
        router: Router,
        device: Device,
        limit_mbps: Decimal,
    ) -> RouterActionResult:
        if limit_mbps <= 0:
            return RouterActionResult(
                success=False,
                action_type="bandwidth_limit",
                status="failed",
                message="Bandwidth limit must be greater than 0.",
                error_message="Invalid bandwidth limit.",
            )

        return RouterActionResult(
            success=True,
            action_type="bandwidth_limit",
            status="success",
            message="Simulated bandwidth limit applied successfully.",
            response_payload={
                "adapter": self.adapter_name,
                "router_id": str(router.id),
                "device_id": str(device.id),
                "limit_mbps": str(limit_mbps),
            },
        )

    async def apply_device_priority(
        self,
        *,
        router: Router,
        device: Device,
        priority_level: int,
    ) -> RouterActionResult:
        if priority_level < 1 or priority_level > 10:
            return RouterActionResult(
                success=False,
                action_type="device_priority",
                status="failed",
                message="Priority level must be between 1 and 10.",
                error_message="Invalid priority level.",
            )

        return RouterActionResult(
            success=True,
            action_type="device_priority",
            status="success",
            message="Simulated device priority applied successfully.",
            response_payload={
                "adapter": self.adapter_name,
                "router_id": str(router.id),
                "device_id": str(device.id),
                "priority_level": priority_level,
            },
        )


simulator_router_adapter: RouterAdapter = SimulatorRouterAdapter()
