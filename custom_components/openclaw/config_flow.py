from __future__ import annotations

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .api import OpenClawApi, OpenClawAuthError, OpenClawConnectionError
from .const import (
    CONF_AGENT_ID,
    CONF_API_TOKEN,
    CONF_BASE_URL,
    CONF_SCAN_INTERVAL,
    DEFAULT_AGENT_ID,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate auth is invalid."""


async def _validate_input(data: dict) -> None:
    session = aiohttp.ClientSession()
    try:
        api = OpenClawApi(
            base_url=data[CONF_BASE_URL],
            api_token=data[CONF_API_TOKEN],
            agent_id=data.get(CONF_AGENT_ID, DEFAULT_AGENT_ID),
            session=session,
        )
        await api.health()
    except OpenClawAuthError as err:
        raise InvalidAuth from err
    except OpenClawConnectionError as err:
        raise CannotConnect from err
    except Exception as err:
        raise CannotConnect from err
    finally:
        await session.close()


class OpenClawConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry):
        return OpenClawOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}

        if user_input is not None:
            try:
                await _validate_input(user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title="OpenClaw", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_BASE_URL): str,
                vol.Required(CONF_API_TOKEN): str,
                vol.Optional(CONF_AGENT_ID, default=DEFAULT_AGENT_ID): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_reauth(self, entry_data: dict[str, str]) -> FlowResult:
        self._reauth_entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None) -> FlowResult:
        errors = {}

        if user_input is not None:
            merged = {
                **self._reauth_entry.data,
                CONF_API_TOKEN: user_input[CONF_API_TOKEN],
            }
            try:
                await _validate_input(merged)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                errors["base"] = "unknown"
            else:
                self.hass.config_entries.async_update_entry(self._reauth_entry, data=merged)
                await self.hass.config_entries.async_reload(self._reauth_entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        schema = vol.Schema({vol.Required(CONF_API_TOKEN): str})
        return self.async_show_form(step_id="reauth_confirm", data_schema=schema, errors=errors)


class OpenClawOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=3600)),
                vol.Optional(
                    CONF_AGENT_ID,
                    default=self.config_entry.options.get(
                        CONF_AGENT_ID,
                        self.config_entry.data.get(CONF_AGENT_ID, DEFAULT_AGENT_ID),
                    ),
                ): str,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
