"""Sensor platform for Swtch EV Charger."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfElectricCurrent, UnitOfElectricPotential, UnitOfPower
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
    interface: str | None = None
    interface_field: str | None = None


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
    SwtchSensorDescription(
        key="ethernet_ip",
        name="Ethernet IP",
        interface="eth0",
        interface_field="ip",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SwtchSensorDescription(
        key="ethernet_dns",
        name="Ethernet DNS",
        interface="eth0",
        interface_field="dns",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SwtchSensorDescription(
        key="ethernet_gateway",
        name="Ethernet Gateway",
        interface="eth0",
        interface_field="gateway",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SwtchSensorDescription(
        key="ethernet_netmask",
        name="Ethernet Netmask",
        interface="eth0",
        interface_field="netmask",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SwtchSensorDescription(
        key="ethernet_mac_address",
        name="Ethernet MAC Address",
        interface="eth0",
        interface_field="macAddress",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SwtchSensorDescription(
        key="ethernet_state",
        name="Ethernet State",
        interface="eth0",
        interface_field="state",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SwtchSensorDescription(
        key="ethernet_online",
        name="Ethernet Online",
        interface="eth0",
        interface_field="isOnline",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SwtchSensorDescription(
        key="wifi_ip",
        name="Wi-Fi IP",
        interface="wlan0",
        interface_field="ip",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SwtchSensorDescription(
        key="wifi_signal",
        name="Wi-Fi Signal",
        interface="wlan0",
        interface_field="dbm",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement="dBm",
        state_class=SensorStateClass.MEASUREMENT,
        value_type="float",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SwtchSensorDescription(
        key="wifi_dns",
        name="Wi-Fi DNS",
        interface="wlan0",
        interface_field="dns",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SwtchSensorDescription(
        key="wifi_gateway",
        name="Wi-Fi Gateway",
        interface="wlan0",
        interface_field="gateway",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SwtchSensorDescription(
        key="wifi_netmask",
        name="Wi-Fi Netmask",
        interface="wlan0",
        interface_field="netmask",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SwtchSensorDescription(
        key="wifi_mac_address",
        name="Wi-Fi MAC Address",
        interface="wlan0",
        interface_field="macAddress",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SwtchSensorDescription(
        key="wifi_state",
        name="Wi-Fi State",
        interface="wlan0",
        interface_field="state",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SwtchSensorDescription(
        key="wifi_online",
        name="Wi-Fi Online",
        interface="wlan0",
        interface_field="isOnline",
        entity_category=EntityCategory.DIAGNOSTIC,
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

        if desc.interface and desc.interface_field:
            interfaces = nested_get(data, ("_network", "data", "info", "ifaceDetails"), [])
            if isinstance(interfaces, list):
                value = next(
                    (
                        interface.get(desc.interface_field)
                        for interface in interfaces
                        if isinstance(interface, dict)
                        and interface.get("name") == desc.interface
                    ),
                    None,
                )
            else:
                value = None
        else:
            value = nested_get(data, desc.path)

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

        if value is None:
            return None

        if desc.value_type == "float":
            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        return value
