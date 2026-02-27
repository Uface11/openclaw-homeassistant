from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_AGENT_ID, CONF_API_TOKEN, CONF_BASE_URL, DEFAULT_AGENT_ID, DOMAIN


class OpenClawConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="OpenClaw", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_BASE_URL): str,
                vol.Required(CONF_API_TOKEN): str,
                vol.Optional(CONF_AGENT_ID, default=DEFAULT_AGENT_ID): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
