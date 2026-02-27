from __future__ import annotations

import aiohttp
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady

from .api import OpenClawApi, OpenClawAuthError, OpenClawConnectionError
from .const import (
    CONF_AGENT_ID,
    CONF_API_TOKEN,
    CONF_BASE_URL,
    CONF_SCAN_INTERVAL,
    DEFAULT_AGENT_ID,
    DEFAULT_SCAN_INTERVAL,
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
    effective_agent_id = entry.options.get(CONF_AGENT_ID, entry.data.get(CONF_AGENT_ID, DEFAULT_AGENT_ID))
    scan_interval = int(entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))

    api = OpenClawApi(
        base_url=entry.data[CONF_BASE_URL],
        api_token=entry.data[CONF_API_TOKEN],
        agent_id=effective_agent_id,
        session=session,
    )
    coordinator = OpenClawCoordinator(hass, api, scan_interval=scan_interval)
    try:
        await coordinator.async_config_entry_first_refresh()
    except OpenClawAuthError as err:
        await session.close()
        raise ConfigEntryAuthFailed("Invalid OpenClaw API token") from err
    except OpenClawConnectionError as err:
        await session.close()
        raise ConfigEntryNotReady("Cannot connect to OpenClaw Gateway") from err
    except Exception as err:
        await session.close()
        raise ConfigEntryNotReady(f"OpenClaw setup failed: {err}") from err

    unsub_options_listener = entry.add_update_listener(_async_update_listener)

    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
        "session": session,
        "unsub_options_listener": unsub_options_listener,
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


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id)
        data["unsub_options_listener"]()
        await data["session"].close()
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, SERVICE_SEND_MESSAGE)
            hass.services.async_remove(DOMAIN, SERVICE_RUN_TASK)
            hass.services.async_remove(DOMAIN, SERVICE_REFRESH_STATUS)
            hass.services.async_remove(DOMAIN, SERVICE_HEALTH_CHECK)
    return unload_ok
