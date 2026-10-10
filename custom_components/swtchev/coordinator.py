"""Data update coordinator for Swtch EV Charger."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SwtchApiAuthError, SwtchApiClient, SwtchApiConnectionError, SwtchApiError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class SwtchDataUpdateCoordinator(DataUpdateCoordinator[dict]):
    """Manage fetching charger data."""

    def __init__(self, hass: HomeAssistant, api: SwtchApiClient, scan_interval: int) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.api = api

    async def _async_update_data(self) -> dict:
        """Fetch data from API endpoint."""
        try:
            station_info, network_info = await asyncio.gather(
                self.api.async_get_station_info(),
                self.api.async_get_network_info(),
            )
            if not isinstance(station_info, dict) or not isinstance(network_info, dict):
                raise UpdateFailed("Charger returned an invalid response")
            return {**station_info, "_network": network_info}
        except SwtchApiAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except SwtchApiConnectionError as err:
            raise UpdateFailed(str(err)) from err
        except SwtchApiError as err:
            raise UpdateFailed(f"API error: {err}") from err
