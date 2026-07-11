"""The Swtch EV Charger integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_TIMEOUT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SwtchApiClient
from .const import CONF_SCAN_INTERVAL, DOMAIN, PLATFORMS
from .coordinator import SwtchDataUpdateCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Swtch EV from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    session = async_get_clientsession(hass)
    api = SwtchApiClient(
        session=session,
        host=entry.data[CONF_HOST],
        timeout=entry.options.get(CONF_TIMEOUT, entry.data[CONF_TIMEOUT]),
    )
    coordinator = SwtchDataUpdateCoordinator(
        hass=hass,
        api=api,
        scan_interval=entry.options.get(
            CONF_SCAN_INTERVAL, entry.data[CONF_SCAN_INTERVAL]
        ),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
