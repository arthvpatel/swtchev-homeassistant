# Swtch EV Charger for Home Assistant

A HACS custom integration for Swtch / Joint Tech EVL007 chargers using the charger's local API.

## Features

- UI config flow for:
  - IP address
  - Admin password, only if the charger requires one (the integration logs in and renews its token automatically)
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
  - Meter Raw (disabled by default)
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
6. Enter the charger IP address, scan interval, and timeout.
7. If the charger requires a login (newer firmware), confirm the admin password. It is pre-filled with the charger's factory password; replace it if you changed the password. Chargers on older firmware need no password and skip this step.

## Authentication

Setup first tries the charger without a password, as older firmware needs none. If the charger rejects that, the integration asks for the admin password. If a charger set up without a password later starts requiring one (for example after a firmware update), Home Assistant asks for it through a reauthentication prompt.

With a password, the integration logs in to the charger the same way its web interface does and gets a new access token before the current one expires (tokens last 24 hours). During setup, it reads the factory admin password from the charger web interface, which logs in with it automatically, and pre-fills the password field. If you changed the password, enter yours instead.

Anyone on your network can use the factory password to control the charger. Consider changing it in the charger web interface, then entering the new password in Home Assistant under **Configure**.

The charger accepts only one login session at a time. Opening the charger web interface logs Home Assistant out, and the integration then logs back in on its next poll, which may in turn log the browser out. This is expected.

The login request is encrypted with a key built into the charger's web interface (firmware v1.3.57). If a login is rejected, the integration reads the key from the charger web interface in case a firmware update changed it. A firmware update that changes how the login works could still stop it from working.

### Finding the factory password

If setup says it couldn't read the factory password, you can find it yourself:

1. In a browser, open `view-source:http://<charger-ip>/`.
2. Click the script link in the page, for example `/assets/index-CnGe0hkn.js`. The name changes between firmware versions.
3. Search the script (Ctrl+F) for `username:"admin",password:"`. The factory password is the text between the quotes right after it.

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
  webui.py
  en.json
```

## Notes

- The charger payload uses the original `availablity` spelling, so the integration intentionally reads that field name.
- The charger API and authentication behavior can change after a vendor firmware update.
