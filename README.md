# Swtch EV Charger for Home Assistant

A HACS custom integration for Swtch / Joint Tech EVL007 chargers using the charger's local API.

## Install

1. Push this repo to GitHub with the `custom_components/swtchev/` folder intact.
2. Add the repo to HACS as a custom repository of type **Integration**.
3. Install **Swtch EV Charger**.
4. Restart Home Assistant.
5. Add the integration from **Settings -> Devices & Services**.

## Notes

- The charger API field is `availablity`, not `availability`, and this integration preserves that device-side spelling.
- Options let you change scan interval and timeout after setup.
