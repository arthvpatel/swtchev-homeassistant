# Swtch EV Charger for Home Assistant

A HACS custom integration for Swtch / Joint Tech EVL007 chargers using the charger's local API.

## Features

- UI config flow for:
  - IP address
  - Admin password (the integration logs in and renews its token automatically)
  - Scan interval (seconds)
  - Timeout (seconds)
- Polls `http://<charger-ip>/api/GetChargingStationInfo`
- Polls `http://<charger-ip>/api/GetNetworkInfo` and exposes non-sensitive interface
  details as diagnostic sensors. Credentials and OCPP profile data are not exposed.
- Creates sensors for:
  - Status
  - CP Status
  - Voltage
  - Current
  - Power
  - Meter Raw
  - Energy (cumulative meter reading)
  - Firmware
  - Mode
- Creates diagnostic sensors for Ethernet and Wi-Fi network details:
  - IP address
  - Signal strength
  - DNS, gateway, and netmask
  - MAC address
  - Interface state and online status
- Creates binary sensors for:
  - Online
  - Occupied
  - Connected
  - Active

## Repository layout

Upload this repository with the `custom_components/swtchev/` folder intact.


## Installation

1. In HACS, add this repository as a custom repository of type **Integration**.
2. Download **Swtch EV Charger**.
3. Restart Home Assistant.
4. Go to **Settings -> Devices & services -> Add integration**.
5. Search for **Swtch EV Charger**.
6. Enter the charger IP address, admin password, scan interval, and timeout.

## Authentication

Enter the charger's **admin password** during setup. The integration logs in to the charger the same way its web interface does and gets a new access token before the current one expires (tokens last 24 hours). If you have never changed the password, use the charger's factory admin password; the charger web interface logs in with it automatically when you open it.

Anyone on your network can use the factory password to control the charger. Consider changing it in the charger web interface, then entering the new password in Home Assistant under **Configure**.

The charger accepts only one login session at a time. Opening the charger web interface logs Home Assistant out, and the integration then logs back in on its next poll, which may in turn log the browser out. This is expected.

The login request is encrypted with keys built into the charger's web interface (firmware v1.3.x). A firmware update could change this and stop the login from working.

## Updating the password

If you change the charger password:

1. In Home Assistant, open **Settings -> Devices & services -> Swtch EV Charger**.
2. Select **Configure**.
3. Enter the new password and submit the form. The integration reloads automatically.

## Polling guidance

Start with a scan interval of **300 seconds**. Some EVL007 firmware revisions can become unreliable when polled too frequently, so reduce the interval only after confirming stable behaviour.

## Hourly energy usage

The **Energy** sensor reports the charger's cumulative `Meter` register (in 0.1 Wh, displayed as kWh) with Home Assistant's `total_increasing` energy state class. For example, a meter reading of `332509.00` is shown as `33.3 kWh`. Home Assistant records hourly long-term statistics for it automatically, so you can add it to the Energy dashboard under **Settings → Dashboards → Energy → Individual devices** to see hourly usage. If you want a sensor that resets every hour, day, or month, create a Utility Meter helper with this sensor as its source.

## Security notes

- The password grants access to the charger’s local API. Handle it as a credential.
- The API is local HTTP, not HTTPS, so keep the charger on a trusted LAN/VLAN and do not expose it to the internet.
- This integration does not log the password or its access token.
- The password is entered through the Home Assistant UI; never hard-code it in repository files.

## Repository layout

```text
custom_components/swtchev/
  __init__.py
  api.py
  binary_sensor.py
  config_flow.py
  const.py
  coordinator.py
  crypto.py
  entity.py
  helpers.py
  manifest.json
  sensor.py
  strings.json
  en.json
```

## Notes

- The charger payload uses the original `availablity` spelling, so the integration intentionally reads that field name.
- The charger API and authentication behavior can change after a vendor firmware update.
