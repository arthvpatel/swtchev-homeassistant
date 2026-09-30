"""API client for Swtch / Joint Tech EVL007 chargers."""

from __future__ import annotations

import asyncio
import base64
import json
import time
from typing import Any

import aiohttp

from .const import DEFAULT_USERNAME
from .crypto import encrypt_body
from .helpers import nested_get

# Log in again this many seconds before the access token expires
TOKEN_RENEW_MARGIN = 300


class SwtchApiError(Exception):
    """Base error for the Swtch API client."""


class SwtchApiConnectionError(SwtchApiError):
    """Raised when the charger cannot be reached."""


class SwtchApiResponseError(SwtchApiError):
    """Raised when the charger returns an unexpected response."""


class SwtchApiAuthError(SwtchApiError):
    """Raised when the token is missing, invalid, or expired."""


class SwtchApiClient:
    """Client for the Swtch/Joint Tech local charger API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        timeout: int = 10,
        token: str | None = None,
        password: str | None = None,
        username: str = DEFAULT_USERNAME,
    ) -> None:
        """Initialize the API client.

        With a password, the client logs in and renews the token by itself.
        Without one, it uses the given token as-is.
        """
        self.session = session
        self.host = host
        self.timeout = timeout
        self.token = token
        self.username = username
        self.password = password
        self._token_expiry = _token_expiry(token)

    def _headers(self) -> dict[str, str]:
        """Build request headers, including auth if a token is set."""
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def _request(
        self, method: str, path: str, body: Any = None, error_body_ok: bool = False
    ) -> Any:
        """Perform a request against the charger's local API.

        With error_body_ok, a 500 response is returned as JSON too, since the
        charger reports login failures that way.
        """
        url = f"http://{self.host}/api{path}"
        try:
            async with self.session.request(
                method,
                url,
                headers=self._headers(),
                json=body,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            ) as resp:
                if resp.status == 401:
                    raise SwtchApiAuthError(
                        "Authorization header required or token rejected"
                    )
                if resp.status != 200 and not (error_body_ok and resp.status == 500):
                    raise SwtchApiResponseError(
                        f"Unexpected status {resp.status} from {path}"
                    )
                try:
                    return await resp.json(content_type=None)
                except ValueError as err:
                    raise SwtchApiResponseError(
                        f"Invalid JSON response from {path}"
                    ) from err
        except asyncio.TimeoutError as err:
            raise SwtchApiConnectionError(
                f"Timed out connecting to charger at {self.host}"
            ) from err
        except aiohttp.ClientError as err:
            raise SwtchApiConnectionError(
                f"Error connecting to charger at {self.host}: {err}"
            ) from err

    async def async_login(self) -> None:
        """Log in with the password and store the new access token."""
        self.token = None
        result = await self._request(
            "POST",
            "/Login",
            encrypt_body({"username": self.username, "password": self.password}),
            error_body_ok=True,
        )
        token = nested_get(result, ("data", "accessToken"))
        if nested_get(result, ("code",)) != 200 or not isinstance(token, str):
            raise SwtchApiAuthError(
                f"Login rejected: {nested_get(result, ('msg',), 'no message')}"
            )
        self.token = token
        self._token_expiry = _token_expiry(token)

    async def _get(self, path: str) -> Any:
        """Perform an authenticated GET, logging in again when needed."""
        if self.password and (
            not self.token
            or (
                self._token_expiry is not None
                and time.time() > self._token_expiry - TOKEN_RENEW_MARGIN
            )
        ):
            await self.async_login()
        try:
            return await self._request("GET", path)
        except SwtchApiAuthError:
            if not self.password:
                raise
        # The token was rejected before its expiry (e.g. charger reboot); retry once
        await self.async_login()
        return await self._request("GET", path)

    async def async_get_station_info(self) -> Any:
        """Fetch charging station info."""
        return await self._get("/GetChargingStationInfo")

    async def async_get_network_info(self) -> Any:
        """Fetch network info."""
        return await self._get("/GetNetworkInfo")


def _token_expiry(token: str | None) -> float | None:
    """Read the expiry time from a JWT without verifying it."""
    if not token:
        return None
    try:
        payload = token.split(".")[1]
        claims = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
        return float(claims["exp"])
    except (IndexError, KeyError, TypeError, ValueError):
        return None
