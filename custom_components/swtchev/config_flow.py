"""Config flow for Swtch EV Charger."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_TIMEOUT
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
    TextSelectorConfig,
)

from .api import (
    SwtchApiAuthError,
    SwtchApiClient,
    SwtchApiConnectionError,
    SwtchApiError,
    SwtchApiResponseError,
)
from .const import (
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TIMEOUT,
    DOMAIN,
)
from .webui import WebUiSettings, async_fetch_settings


def build_user_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Build the connection form schema."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(CONF_HOST, default=defaults.get(CONF_HOST, "")): TextSelector(
                TextSelectorConfig(type="text")
            ),
            vol.Required(
                CONF_SCAN_INTERVAL,
                default=defaults.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            ): NumberSelector(
                NumberSelectorConfig(min=5, max=3600, step=1, mode=NumberSelectorMode.BOX)
            ),
            vol.Required(
                CONF_TIMEOUT,
                default=defaults.get(CONF_TIMEOUT, DEFAULT_TIMEOUT),
            ): NumberSelector(
                NumberSelectorConfig(min=1, max=120, step=1, mode=NumberSelectorMode.BOX)
            ),
        }
    )


def build_password_schema(password: str) -> vol.Schema:
    """Build the password form schema."""
    return vol.Schema(
        {
            vol.Required(CONF_PASSWORD, default=password): TextSelector(
                TextSelectorConfig(type="password")
            ),
        }
    )


class SwtchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Swtch EV Charger."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the flow."""
        self._connection: dict[str, Any] = {}
        self._web_ui: WebUiSettings | None = None

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Ask for the charger address and polling settings."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = str(user_input[CONF_HOST]).strip()
            timeout = int(user_input[CONF_TIMEOUT])

            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()

            # Read the factory password the web UI logs in with, to pre-fill it
            settings = await async_fetch_settings(
                async_get_clientsession(self.hass), host, timeout
            )
            if settings is None:
                errors["base"] = "cannot_connect"
            else:
                self._connection = {
                    CONF_HOST: host,
                    CONF_SCAN_INTERVAL: int(user_input[CONF_SCAN_INTERVAL]),
                    CONF_TIMEOUT: timeout,
                }
                self._web_ui = settings
                return await self.async_step_password()

            user_input[CONF_HOST] = host

        return self.async_show_form(
            step_id="user",
            data_schema=build_user_schema(user_input),
            errors=errors,
        )

    async def async_step_password(self, user_input: dict[str, Any] | None = None):
        """Ask for the admin password, pre-filled with the factory one."""
        errors: dict[str, str] = {}

        if user_input is not None:
            password = str(user_input[CONF_PASSWORD]).strip()
            host = self._connection[CONF_HOST]
            client = SwtchApiClient(
                session=async_get_clientsession(self.hass),
                host=host,
                password=password,
                timeout=self._connection[CONF_TIMEOUT],
            )
            client.use_web_ui_settings(self._web_ui)

            try:
                await client.async_get_station_info()
            except SwtchApiAuthError:
                errors["base"] = "invalid_auth"
            except SwtchApiConnectionError:
                errors["base"] = "cannot_connect"
            except SwtchApiResponseError:
                errors["base"] = "invalid_response"
            except SwtchApiError:
                errors["base"] = "unknown"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=f"Swtch EV Charger ({host})",
                    data={**self._connection, CONF_PASSWORD: password},
                )

        factory_password = self._web_ui.password or ""
        return self.async_show_form(
            # Separate step texts, so the form says when the password was not found
            step_id="password" if factory_password else "password_not_found",
            data_schema=build_password_schema(factory_password),
            errors=errors,
        )

    async def async_step_password_not_found(
        self, user_input: dict[str, Any] | None = None
    ):
        """Ask for the admin password when the factory one was not found."""
        return await self.async_step_password(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get options flow."""
        return SwtchOptionsFlowHandler(config_entry)


class SwtchOptionsFlowHandler(config_entries.OptionsFlowWithReload):
    """Handle options flow."""

    def __init__(self, config_entry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage the integration options."""
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={
                    CONF_PASSWORD: str(user_input[CONF_PASSWORD]).strip(),
                    CONF_SCAN_INTERVAL: int(user_input[CONF_SCAN_INTERVAL]),
                    CONF_TIMEOUT: int(user_input[CONF_TIMEOUT]),
                },
            )

        current = {
            CONF_PASSWORD: self._config_entry.options.get(
                CONF_PASSWORD, self._config_entry.data.get(CONF_PASSWORD, "")
            ),
            CONF_SCAN_INTERVAL: self._config_entry.options.get(
                CONF_SCAN_INTERVAL,
                self._config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            ),
            CONF_TIMEOUT: self._config_entry.options.get(
                CONF_TIMEOUT,
                self._config_entry.data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT),
            ),
        }

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_PASSWORD, default=current[CONF_PASSWORD]
                ): TextSelector(TextSelectorConfig(type="password")),
                vol.Required(
                    CONF_SCAN_INTERVAL, default=current[CONF_SCAN_INTERVAL]
                ): NumberSelector(
                    NumberSelectorConfig(min=5, max=3600, step=1, mode=NumberSelectorMode.BOX)
                ),
                vol.Required(CONF_TIMEOUT, default=current[CONF_TIMEOUT]): NumberSelector(
                    NumberSelectorConfig(min=1, max=120, step=1, mode=NumberSelectorMode.BOX)
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
