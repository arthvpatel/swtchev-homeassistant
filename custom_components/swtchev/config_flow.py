"""Config flow for Swtch EV Charger."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_TIMEOUT
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import NumberSelector, NumberSelectorConfig, NumberSelectorMode, TextSelector, TextSelectorConfig

from .api import SwtchApiClient, SwtchApiConnectionError, SwtchApiError, SwtchApiResponseError
from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DEFAULT_TIMEOUT, DOMAIN


def build_user_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Build the config form schema."""
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


class SwtchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Swtch EV Charger."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = str(user_input[CONF_HOST]).strip()
            scan_interval = int(user_input[CONF_SCAN_INTERVAL])
            timeout = int(user_input[CONF_TIMEOUT])

            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)
            client = SwtchApiClient(session=session, host=host, timeout=timeout)

            try:
                await client.async_get_station_info()
            except SwtchApiConnectionError:
                errors["base"] = "cannot_connect"
            except SwtchApiResponseError:
                errors["base"] = "invalid_response"
            except SwtchApiError:
                errors["base"] = "unknown"
            except Exception:
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=f"Swtch EV Charger ({host})",
                    data={
                        CONF_HOST: host,
                        CONF_SCAN_INTERVAL: scan_interval,
                        CONF_TIMEOUT: timeout,
                    },
                )

            user_input[CONF_HOST] = host

        return self.async_show_form(
            step_id="user",
            data_schema=build_user_schema(user_input),
            errors=errors,
        )

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
                    CONF_SCAN_INTERVAL: int(user_input[CONF_SCAN_INTERVAL]),
                    CONF_TIMEOUT: int(user_input[CONF_TIMEOUT]),
                },
            )

        current = {
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
