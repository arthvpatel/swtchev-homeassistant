"""Sensor platform for Swtch EV Charger."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricCurrent, UnitOfElectricPotential, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
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
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    SwtchSensorDescription(
        key="voltage",
        name="Voltage",
        path=("data", "csInfo", "evses", 0, "connectors", 0, "voltage"),
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
        state_class=SensorStateClass.MEASUREMENT,
        value_type="float",
        entity_registry_visible_default=False,
    ),
    SwtchSensorDescription(
        key="current",
        name="Current",
        path=("data", "csInfo", "evses", 0, "connectors", 0, "current"),
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
        value_type="float",
        entity_registry_visible_default=False,
    ),
    SwtchSensorDescription(
        key="power",
        name="Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_unit_of_measurement=UnitOfPower.KILO_WATT, # Show power in kW by default without changing the math
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
        value_type="power",
    ),
    SwtchSensorDescription(
        key="meter_raw",
        name="Meter Raw",
        path=("data", "csInfo", "evses", 0, "connectors", 0, "Meter"),
        suggested_display_precision=0,
        state_class=SensorStateClass.MEASUREMENT,
        value_type="int", # meter_raw is presented as a float, but decimals are always zero
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SwtchSensorDescription(
        key="firmware",
        name="Firmware",
        path=("data", "csInfo", "chargingStation", "firmwareVersion"),
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SwtchSensorDescription(
        key="mode",
        name="Mode",
        path=("data", "csInfo", "chargingMode"),
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
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

        if desc.value_type == "int":
            try:
                return round(float(value))
            except (TypeError, ValueError):
                return None

        return value
