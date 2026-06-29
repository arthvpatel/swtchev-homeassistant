"""Data update coordinator for Swtch EV Charger."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SwtchApiClient, SwtchApiConnectionError, SwtchApiError
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
            return await self.api.async_get_station_info()
        except SwtchApiConnectionError as err:
            raise UpdateFailed(str(err)) from err
        except SwtchApiError as err:
            raise UpdateFailed(f"API error: {err}") from err
