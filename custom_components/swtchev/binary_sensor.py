"""Binary sensor platform for Swtch EV Charger."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SwtchCoordinatorEntity
from .helpers import nested_get


@dataclass(frozen=True, kw_only=True)
class SwtchBinarySensorDescription(BinarySensorEntityDescription):
    """Describe Swtch binary sensor entity."""

    value_type: str
    path: tuple = ()


BINARY_SENSORS: tuple[SwtchBinarySensorDescription, ...] = (
    SwtchBinarySensorDescription(
        key="online",
        name="Online",
        path=("data", "csInfo", "isOnline"),
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_type="bool",
    ),
    SwtchBinarySensorDescription(
        key="occupied",
        name="Occupied",
        path=("data", "csInfo", "isOccupied"),
        value_type="bool",
    ),
    SwtchBinarySensorDescription(
        key="connected",
        name="Connected",
        value_type="connected",
    ),
    SwtchBinarySensorDescription(
        key="active",
        name="Active",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        value_type="active",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Swtch binary sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(
        [SwtchBinarySensorEntity(coordinator, description) for description in BINARY_SENSORS]
    )


class SwtchBinarySensorEntity(SwtchCoordinatorEntity, BinarySensorEntity):
    """Representation of a Swtch binary sensor."""

    entity_description: SwtchBinarySensorDescription

    def __init__(self, coordinator, description: SwtchBinarySensorDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.api.host}_{description.key}"

    @property
    def is_on(self):
        """Return binary sensor state."""
        data = self.coordinator.data or {}
        desc = self.entity_description

        if desc.value_type == "bool":
            return bool(nested_get(data, desc.path, False))

        if desc.value_type == "connected":
            cp_status = nested_get(
                data, ("data", "csInfo", "evses", 0, "connectors", 0, "cpStatus")
            )
            if cp_status is None:
                return None
            return cp_status not in ["Available", "Unavailable"]

        if desc.value_type == "active":
            current = nested_get(
                data, ("data", "csInfo", "evses", 0, "connectors", 0, "current"), 0
            )
            try:
                return float(current) > 0.2
            except (TypeError, ValueError):
                return None

        return None
