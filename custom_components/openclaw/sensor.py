from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([OpenClawStatusSensor(coordinator)], True)


class OpenClawStatusSensor(CoordinatorEntity, SensorEntity):
    _attr_name = "OpenClaw Status"
    _attr_unique_id = "openclaw_status"

    @property
    def native_value(self):
        return "online" if self.coordinator.last_update_success else "offline"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        return {
            "last_response": data.get("lastResponse"),
            "active_sessions": data.get("activeSessions"),
        }
