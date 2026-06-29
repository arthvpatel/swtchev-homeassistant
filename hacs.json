"""Sensor platform for Swtch EV Charger."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricCurrent, UnitOfElectricPotential, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SwtchCoordinatorEntity
from .helpers import nested_get


@dataclass(frozen=True, kw_only=True)
class SwtchSensorDescription(SensorEntityDescription):
    """Describe Swtch sensor entity."""

    path: tuple = ()
    value_type: str = "raw"


SENSORS: tuple[SwtchSensorDescription, ...] = (
    SwtchSensorDescription(
        key="status",
        name="Status",
        path=("data", "csInfo", "evses", 0, "connectors", 0, "availablity"),
    ),
    SwtchSensorDescription(
        key="cp_status",
        name="CP Status",
        path=("data", "csInfo", "evses", 0, "connectors", 0, "cpStatus"),
    ),
    SwtchSensorDescription(
        key="voltage",
        name="Voltage",
        path=("data", "csInfo", "evses", 0, "connectors", 0, "voltage"),
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        value_type="float",
    ),
    SwtchSensorDescription(
        key="current",
        name="Current",
        path=("data", "csInfo", "evses", 0, "connectors", 0, "current"),
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        value_type="float",
    ),
    SwtchSensorDescription(
        key="power",
        name="Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_type="power",
    ),
    SwtchSensorDescription(
        key="meter_raw",
        name="Meter Raw",
        path=("data", "csInfo", "evses", 0, "connectors", 0, "Meter"),
        value_type="float",
    ),
    SwtchSensorDescription(
        key="firmware",
        name="Firmware",
        path=("data", "csInfo", "chargingStation", "firmwareVersion"),
    ),
    SwtchSensorDescription(
        key="mode",
        name="Mode",
        path=("data", "csInfo", "chargingMode"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Swtch sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(
        [SwtchSensorEntity(coordinator, description) for description in SENSORS]
    )


class SwtchSensorEntity(SwtchCoordinatorEntity, SensorEntity):
    """Representation of a Swtch sensor."""

    entity_description: SwtchSensorDescription

    def __init__(self, coordinator, description: SwtchSensorDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.api.host}_{description.key}"

    @property
    def native_value(self):
        """Return sensor value."""
        data = self.coordinator.data or {}
        desc = self.entity_description

        if desc.value_type == "power":
            current = nested_get(
                data, ("data", "csInfo", "evses", 0, "connectors", 0, "current"), 0
            )
            voltage = nested_get(
                data, ("data", "csInfo", "evses", 0, "connectors", 0, "voltage"), 0
            )
            try:
                return round(float(current) * float(voltage), 1)
            except (TypeError, ValueError):
                return None

        value = nested_get(data, desc.path)
        if value is None:
            return None

        if desc.value_type == "float":
            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        return value
