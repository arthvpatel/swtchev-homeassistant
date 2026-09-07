# Swtch EV Charger for Home Assistant

A HACS custom integration for Swtch / Joint Tech EVL007 chargers using the charger's local API.

## Features

- UI config flow for:
  - IP address
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
6. Enter the charger IP address, bearer token, scan interval, and timeout.

## Getting the API token

The token is obtained from the charger web UI in your local network. Treat it like a password: do not share it, paste it into GitHub issues, commit it to this repository, or include it in screenshots.

### Browser method

1. Browse to `http://<charger-ip>`; for example, `http://10.10.10.20`.
2. Sign in to the charger web interface.
3. Press **F12** to open browser Developer Tools.
4. Open **Network** and enable **Preserve log**.
5. Choose the **Fetch/XHR** filter, then refresh the page.
6. Click a successful request such as `GetWifiList`, `GetNetworkInfo`, or `GetChargingStationInfo`.
7. Open **Headers** and find the request header named `Authorization`.
8. Its value will be formatted as:

   ```text
   Bearer eyJ...
   ```

9. Copy only the text after `Bearer ` (the token beginning with `eyJ...`) into the **API token** field during the Home Assistant setup flow.

Do not include the word `Bearer` in the Home Assistant field; the integration adds it automatically.

### Token validation in PowerShell

Before configuring Home Assistant, you can test the token from a machine on the same network:

```powershell
$ip = "10.10.10.20"
$token = "PASTE_TOKEN_HERE"

curl.exe -sS `
  -H "Accept: application/json" `
  -H "Authorization: Bearer $token" `
  "http://$ip/api/GetChargingStationInfo"
```

A working token returns JSON station data. A response containing HTTP `401` means the token is invalid, expired, missing, or copied with extra text.

## Updating a token

If the charger UI logs you out or the integration displays an authentication error:

1. Obtain a new token using the browser method above.
2. In Home Assistant, open **Settings -> Devices & services -> Swtch EV Charger**.
3. Select **Configure**.
4. Replace the API token and submit the form. The integration reloads automatically.

## Polling guidance

Start with a scan interval of **300 seconds**. Some EVL007 firmware revisions can become unreliable when polled too frequently, so reduce the interval only after confirming stable behaviour.

## Security notes

- The token grants access to the charger’s local API. Handle it as a credential.
- The API is local HTTP, not HTTPS, so keep the charger on a trusted LAN/VLAN and do not expose it to the internet.
- This integration does not log the token.
- The token is entered through the Home Assistant UI; never hard-code it in repository files.

## Repository layout

```text
custom_components/swtchev/
  __init__.py
  api.py
  binary_sensor.py
  config_flow.py
  const.py
  coordinator.py
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
