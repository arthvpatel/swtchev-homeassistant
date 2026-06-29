# Swtch EV Charger for Home Assistant

A HACS custom integration for Swtch / Joint Tech EVL007 chargers using the charger's local API.

## Features

- UI config flow for:
  - IP address
  - Scan interval (seconds)
  - Timeout (seconds)
- Polls `http://<charger-ip>/api/GetChargingStationInfo`
- Creates sensors for:
  - Status
  - CP Status
  - Voltage
  - Current
  - Power
  - Meter Raw
  - Firmware
  - Mode
- Creates binary sensors for:
  - Online
  - Occupied
  - Connected
  - Active

## Repository layout

Upload this repository with the `custom_components/swtchev/` folder intact.

## Installation with HACS

1. Add this repository to HACS as a custom repository of type **Integration**.
2. Install **Swtch EV Charger** from HACS.
3. Restart Home Assistant.
4. Go to **Settings -> Devices & Services -> Add Integration**.
5. Search for **Swtch EV Charger**.
6. Enter the charger IP address, scan interval, and timeout.

## Notes

- The charger JSON uses the key `availablity` instead of `availability`, so this integration intentionally reads the device's original field name.
- Scan interval and timeout can be changed later from the integration options.
- If future firmware requires authentication, extend `api.py`.
