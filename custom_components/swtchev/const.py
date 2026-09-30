"""Constants for the Swtch EV Charger integration."""

from __future__ import annotations

DOMAIN = "swtchev"
DEFAULT_NAME = "Swtch EV Charger"
DEFAULT_SCAN_INTERVAL = 15
DEFAULT_TIMEOUT = 10

CONF_SCAN_INTERVAL = "scan_interval"
CONF_PASSWORD = "password"

# Account the charger web UI logs in with
DEFAULT_USERNAME = "admin"

PLATFORMS = ["sensor", "binary_sensor"]
