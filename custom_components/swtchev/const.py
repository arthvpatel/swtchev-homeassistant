"""Constants for the Swtch EV Charger integration."""

from __future__ import annotations

DOMAIN = "swtchev"
DEFAULT_NAME = "Swtch EV Charger"
DEFAULT_SCAN_INTERVAL = 15
DEFAULT_TIMEOUT = 10

CONF_SCAN_INTERVAL = "scan_interval"
CONF_PASSWORD = "password"
# kWh the charger app shows, entered to calibrate; turned into an offset (Wh)
CONF_APP_ENERGY = "app_energy"
CONF_RESET_ENERGY = "reset_energy_calibration"
CONF_ENERGY_OFFSET = "energy_offset_wh"

# Account the charger web UI logs in with
DEFAULT_USERNAME = "admin"

PLATFORMS = ["sensor", "binary_sensor"]
