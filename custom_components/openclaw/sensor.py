from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


def _data_root(data):
    if not isinstance(data, dict):
        return {}
    if isinstance(data.get("result"), dict):
        return data["result"]
    return data


def _pick(data: dict, *keys):
    for key in keys:
        val = data.get(key)
        if val is not None:
            return val
    return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(
        [
            OpenClawStatusSensor(coordinator),
            OpenClawActiveSessionsSensor(coordinator),
            OpenClawUsageTokensSensor(coordinator),
            OpenClawCostSensor(coordinator),
            OpenClawUptimeSensor(coordinator),
        ],
        True,
    )


class OpenClawBaseSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    @property
    def root(self):
        return _data_root(self.coordinator.data)

    @property
    def available(self) -> bool:
        return bool(self.coordinator.last_update_success)

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, "gateway")},
            name="OpenClaw Gateway",
            manufacturer="OpenClaw",
            model="Gateway",
        )


class OpenClawStatusSensor(OpenClawBaseSensor):
    _attr_name = "Status"
    _attr_unique_id = "openclaw_status"

    @property
    def native_value(self):
        return "online" if self.coordinator.last_update_success else "offline"


class OpenClawActiveSessionsSensor(OpenClawBaseSensor):
    _attr_name = "Active sessions"
    _attr_unique_id = "openclaw_active_sessions"
    _attr_icon = "mdi:account-multiple"

    @property
    def native_value(self):
        val = _pick(self.root, "activeSessions", "sessions", "sessionCount")
        return val if val is not None else 0


class OpenClawUsageTokensSensor(OpenClawBaseSensor):
    _attr_name = "Usage tokens"
    _attr_unique_id = "openclaw_usage_tokens"
    _attr_icon = "mdi:counter"

    @property
    def native_value(self):
        usage = self.root.get("usage") if isinstance(self.root.get("usage"), dict) else {}
        return _pick(usage, "totalTokens", "tokens", "inputTokens", "outputTokens")


class OpenClawCostSensor(OpenClawBaseSensor):
    _attr_name = "Cost estimate"
    _attr_unique_id = "openclaw_cost_estimate"
    _attr_icon = "mdi:currency-eur"

    @property
    def native_value(self):
        usage = self.root.get("usage") if isinstance(self.root.get("usage"), dict) else {}
        return _pick(usage, "cost", "totalCost", "estimatedCost")


class OpenClawUptimeSensor(OpenClawBaseSensor):
    _attr_name = "Uptime seconds"
    _attr_unique_id = "openclaw_uptime_seconds"
    _attr_icon = "mdi:timer-outline"
    _attr_native_unit_of_measurement = "s"
    _attr_state_class = "measurement"

    @property
    def native_value(self):
        return _pick(self.root, "uptimeSec", "uptimeSeconds", "uptime")
