# EVL007 Charger → Home Assistant

Bring a Joint Tech / EVL007 charger into Home Assistant using the charger's local web API and template sensors.

This project is based on inspection of the charger's local web UI bundle, which shows a local JSON API with calls such as `GetChargingStationInfo`, `GetNetworkInfo`, and OCPP variable reads/writes, plus charger data structures containing `csInfo`, `evses`, `connectors`, `availablity`, `cpStatus`, `voltage`, `current`, `Meter`, `isOnline`, `isOccupied`, firmware, and charging mode fields.[file:1]

## What this does

This setup exposes EVL007 charger data inside Home Assistant with:

- A REST sensor that polls the charger locally.
- Template sensors for live electrical values like voltage, current, and calculated power.
- Binary sensors for online, occupied, connected, and active charging states.
- Lovelace dashboard cards for status, history, and charging trends.

The charger frontend indicates that the local device UI talks directly to a JSON API and reads charger state from `data.csInfo` and per-connector objects, which makes this approach possible without scraping rendered HTML.[file:1]

## Data exposed

The local UI code indicates the charger can expose fields like these through `GetChargingStationInfo`:[file:1]

- Charger online state: `csInfo.isOnline`
- Occupancy state: `csInfo.isOccupied`
- Charging mode: `csInfo.chargingMode`
- Firmware version: `csInfo.chargingStation.firmwareVersion`
- Connector availability: `csInfo.evses[0].connectors[0].availablity`
- Control pilot status: `csInfo.evses[0].connectors[0].cpStatus`
- Voltage: `csInfo.evses[0].connectors[0].voltage`
- Current: `csInfo.evses[0].connectors[0].current`
- Meter value: `csInfo.evses[0].connectors[0].Meter`

The same frontend bundle also shows OCPP variable access for values such as `Voltage`, `ACCurrent`, `EnableCTClamp`, `CTClampLimitCurrent`, `UserLanguage`, and `TimeZone`, which may be useful for future expansion beyond basic telemetry.[file:1]

## Requirements

- Home Assistant with YAML configuration enabled.
- Network access from Home Assistant to the EVL007 charger.
- The charger IP address.
- A charger firmware/API version that exposes the local web API.

The inspected charger bundle shows a local API client with a base URL of `http://10.110.110.2` in that device context, but the actual charger IP in a deployment will be whatever address the charger has on the local network.[file:1]

## Example Home Assistant config

### 1) REST sensor

```yaml
rest:
  - resource: "http://CHARGER_IP/api/GetChargingStationInfo"
    scan_interval: 15
    timeout: 10
    sensor:
      - name: joint_charger_api
        unique_id: joint_charger_api
        value_template: "{{ value_json.code }}"
        json_attributes:
          - data
```

### 2) Template sensors

```yaml
- sensor:
    - name: "Joint Charger Status"
      unique_id: joint_charger_status
      state: "{{ state_attr('sensor.joint_charger_api', 'data').csInfo.evses[0].connectors[0].availablity }}"
      availability: "{{ state_attr('sensor.joint_charger_api', 'data') is not none }}"

    - name: "Joint Charger CP Status"
      unique_id: joint_charger_cp_status
      state: "{{ state_attr('sensor.joint_charger_api', 'data').csInfo.evses[0].connectors[0].cpStatus }}"
      availability: "{{ state_attr('sensor.joint_charger_api', 'data') is not none }}"

    - name: "Joint Charger Voltage"
      unique_id: joint_charger_voltage
      unit_of_measurement: "V"
      device_class: voltage
      state_class: measurement
      state: "{{ state_attr('sensor.joint_charger_api', 'data').csInfo.evses[0].connectors[0].voltage | float(0) }}"
      availability: "{{ state_attr('sensor.joint_charger_api', 'data') is not none }}"

    - name: "Joint Charger Current"
      unique_id: joint_charger_current
      unit_of_measurement: "A"
      device_class: current
      state_class: measurement
      state: "{{ state_attr('sensor.joint_charger_api', 'data').csInfo.evses[0].connectors[0].current | float(0) }}"
      availability: "{{ state_attr('sensor.joint_charger_api', 'data') is not none }}"

    - name: "Joint Charger Power"
      unique_id: joint_charger_power
      unit_of_measurement: "W"
      device_class: power
      state_class: measurement
      state: >
        {% set c = state_attr('sensor.joint_charger_api', 'data').csInfo.evses[0].connectors[0].current | float(0) %}
        {% set v = state_attr('sensor.joint_charger_api', 'data').csInfo.evses[0].connectors[0].voltage | float(0) %}
        {{ (c * v) | round(1) }}
      availability: "{{ state_attr('sensor.joint_charger_api', 'data') is not none }}"

    - name: "Joint Charger Meter Raw"
      unique_id: joint_charger_meter_raw
      state: "{{ state_attr('sensor.joint_charger_api', 'data').csInfo.evses[0].connectors[0].Meter | float(0) }}"
      availability: "{{ state_attr('sensor.joint_charger_api', 'data') is not none }}"

    - name: "Joint Charger Firmware"
      unique_id: joint_charger_firmware
      state: "{{ state_attr('sensor.joint_charger_api', 'data').csInfo.chargingStation.firmwareVersion }}"
      availability: "{{ state_attr('sensor.joint_charger_api', 'data') is not none }}"

    - name: "Joint Charger Mode"
      unique_id: joint_charger_mode
      state: "{{ state_attr('sensor.joint_charger_api', 'data').csInfo.chargingMode }}"
      availability: "{{ state_attr('sensor.joint_charger_api', 'data') is not none }}"

- binary_sensor:
    - name: "Joint Charger Online"
      unique_id: joint_charger_online
      state: "{{ state_attr('sensor.joint_charger_api', 'data').csInfo.isOnline | bool }}"
      availability: "{{ state_attr('sensor.joint_charger_api', 'data') is not none }}"

    - name: "Joint Charger Occupied"
      unique_id: joint_charger_occupied
      state: "{{ state_attr('sensor.joint_charger_api', 'data').csInfo.isOccupied | bool }}"
      availability: "{{ state_attr('sensor.joint_charger_api', 'data') is not none }}"

    - name: "Joint Charger Connected"
      unique_id: joint_charger_connected
      state: >
        {{ state_attr('sensor.joint_charger_api', 'data').csInfo.evses[0].connectors[0].cpStatus not in ['Available', 'Unavailable'] }}
      availability: "{{ state_attr('sensor.joint_charger_api', 'data') is not none }}"

    - name: "Joint Charger Active"
      unique_id: joint_charger_active
      state: >
        {{ (state_attr('sensor.joint_charger_api', 'data').csInfo.evses[0].connectors[0].current | float(0)) > 0.2 }}
      availability: "{{ state_attr('sensor.joint_charger_api', 'data') is not none }}"
```

## Notes and caveats

- The key name `availablity` appears to be misspelled by the charger itself, so templates must use that exact JSON key.[file:1]
- Some firmwares may require authentication. The inspected frontend includes bearer-token handling and an `Authorization` header in the API client, so open local access is not guaranteed on every device.[file:1]
- The local web UI bundle also references additional endpoints like `GetNetworkInfo`, `ListNetworkProfile`, `ListLocalCards`, `ocppGetVariables`, and `ocppSetVariables`, which may allow broader monitoring or configuration in future work.[file:1]
- The meter field is currently treated as raw until its exact units are confirmed from live responses.[file:1]

## Suggested repository structure

```text
.
├── README.md
├── rest.yaml
├── templates/
│   └── evl007.yaml
└── lovelace/
    └── ev_charging_dashboard.yaml
```

## Roadmap

- Confirm authenticated vs unauthenticated API access.
- Validate exact units for `Meter`.
- Add energy dashboard compatibility once meter units are confirmed.
- Expand OCPP variable mapping for configuration entities.
- Optionally turn this into a custom integration.

## Credits

This project was derived by inspecting the charger's local web frontend bundle and mapping its internal API/data structures into Home Assistant-friendly entities.[file:1]
