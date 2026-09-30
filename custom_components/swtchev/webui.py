"""Read login settings from the charger web UI's JavaScript."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import re
from urllib.parse import urljoin

import aiohttp

# "ssh-ed25519" key blobs always start with this base64 prefix
_PUBLIC_KEY_RE = re.compile(r"AAAAC3NzaC1lZDI1NTE5[A-Za-z0-9+/]+=*")
# The IV is the 16-character string checked right before this error message
_IV_RE = re.compile(r'"([^"\\]{16})"[^"]{0,80}"Encrypt salt must be exactly 16 bytes')
# The page logs in automatically with the factory account
_LOGIN_RE = re.compile(r'username\s*:\s*"([^"]+)"\s*,\s*password\s*:\s*"([^"]+)"')
_SCRIPT_RE = re.compile(r"""<script[^>]*\ssrc\s*=\s*["']?([^"'\s>]+)""", re.IGNORECASE)


@dataclass
class WebUiSettings:
    """Login settings found in the web UI; each is None if not found."""

    public_key: str | None = None
    iv: bytes | None = None
    username: str | None = None
    password: str | None = None


def parse_script(script: str) -> WebUiSettings:
    """Extract login settings from the web UI's JavaScript bundle."""
    settings = WebUiSettings()
    if match := _PUBLIC_KEY_RE.search(script):
        settings.public_key = match.group(0)
    if match := _IV_RE.search(script):
        settings.iv = match.group(1).encode()
    if match := _LOGIN_RE.search(script):
        settings.username, settings.password = match.groups()
    return settings


async def async_fetch_settings(
    session: aiohttp.ClientSession, host: str, timeout: int
) -> WebUiSettings | None:
    """Fetch the web UI and return the login settings it contains.

    Returns None if the charger cannot be reached, and empty settings if the
    page does not contain them.
    """
    base = f"http://{host}/"
    client_timeout = aiohttp.ClientTimeout(total=timeout)
    try:
        async with session.get(base, timeout=client_timeout) as resp:
            page = await resp.text()
        for src in _SCRIPT_RE.findall(page):
            url = urljoin(base, src)
            if not url.startswith(base):
                continue
            async with session.get(url, timeout=client_timeout) as resp:
                settings = parse_script(await resp.text())
            if settings.public_key or settings.password:
                return settings
    except (asyncio.TimeoutError, aiohttp.ClientError):
        return None
    return WebUiSettings()
