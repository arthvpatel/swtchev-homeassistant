"""API client for Swtch EV Charger."""

from __future__ import annotations

from asyncio import TimeoutError as AsyncTimeoutError
import socket
from typing import Any

from aiohttp import ClientError, ClientSession


class SwtchApiError(Exception):
    """Base API error."""


class SwtchApiConnectionError(SwtchApiError):
    """Raised when the charger cannot be reached."""


class SwtchApiResponseError(SwtchApiError):
    """Raised when the charger returns invalid data."""


class SwtchApiClient:
    def __init__(self, session: ClientSession, host: str, timeout: int) -> None:
        self._session = session
        self.host = host
        self.timeout = timeout

    @property
    def endpoint(self) -> str:
        return f"http://{self.host}/api/GetChargingStationInfo"

    async def async_get_station_info(self) -> dict[str, Any]:
        try:
            async with self._session.get(self.endpoint, timeout=self.timeout) as response:
                response.raise_for_status()
                payload = await response.json(content_type=None)
        except (ClientError, AsyncTimeoutError, socket.gaierror) as err:
            raise SwtchApiConnectionError(f"Failed to connect to {self.host}: {err}") from err
        except ValueError as err:
            raise SwtchApiResponseError("Invalid JSON received from charger") from err

        if not isinstance(payload, dict):
            raise SwtchApiResponseError("Unexpected API response")
        return payload
