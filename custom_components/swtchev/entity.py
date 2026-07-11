"""Base entity for Swtch EV Charger."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_NAME, DOMAIN
from .helpers import nested_get


class SwtchCoordinatorEntity(CoordinatorEntity):
    """Base coordinator entity."""

    _attr_has_entity_name = True

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        firmware = nested_get(
            self.coordinator.data,
            ("data", "csInfo", "chargingStation", "firmwareVersion"),
        )
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.api.host)},
            name=DEFAULT_NAME,
            manufacturer="Swtch / Joint Tech",
            model="EVL007",
            sw_version=firmware,
            configuration_url=f"http://{self.coordinator.api.host}",
        )
