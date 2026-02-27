from __future__ import annotations

import aiohttp
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall

from .api import OpenClawApi
from .const import (
    CONF_AGENT_ID,
    CONF_API_TOKEN,
    CONF_BASE_URL,
    DEFAULT_AGENT_ID,
    DOMAIN,
    PLATFORMS,
    SERVICE_REFRESH_STATUS,
    SERVICE_HEALTH_CHECK,
    SERVICE_RUN_TASK,
    SERVICE_SEND_MESSAGE,
)
from .coordinator import OpenClawCoordinator

SERVICE_SCHEMA_MESSAGE = vol.Schema({vol.Required("message"): str})
SERVICE_SCHEMA_TASK = vol.Schema({vol.Required("task"): str})


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    session = aiohttp.ClientSession()
    api = OpenClawApi(
        base_url=entry.data[CONF_BASE_URL],
        api_token=entry.data[CONF_API_TOKEN],
        agent_id=entry.data.get(CONF_AGENT_ID, DEFAULT_AGENT_ID),
        session=session,
    )
    coordinator = OpenClawCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
        "session": session,
    }

    async def _send_message(call: ServiceCall) -> None:
        await api.send_message(call.data["message"])

    async def _run_task(call: ServiceCall) -> None:
        await api.run_task(call.data["task"])

    async def _refresh_status(call: ServiceCall) -> None:
        await coordinator.async_request_refresh()

    async def _health_check(call: ServiceCall) -> None:
        await api.health()

    hass.services.async_register(DOMAIN, SERVICE_SEND_MESSAGE, _send_message, schema=SERVICE_SCHEMA_MESSAGE)
    hass.services.async_register(DOMAIN, SERVICE_RUN_TASK, _run_task, schema=SERVICE_SCHEMA_TASK)
    hass.services.async_register(DOMAIN, SERVICE_REFRESH_STATUS, _refresh_status)
    hass.services.async_register(DOMAIN, SERVICE_HEALTH_CHECK, _health_check)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id)
        await data["session"].close()
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, SERVICE_SEND_MESSAGE)
            hass.services.async_remove(DOMAIN, SERVICE_RUN_TASK)
            hass.services.async_remove(DOMAIN, SERVICE_REFRESH_STATUS)
            hass.services.async_remove(DOMAIN, SERVICE_HEALTH_CHECK)
    return unload_ok
