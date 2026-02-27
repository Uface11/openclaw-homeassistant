from __future__ import annotations

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import OpenClawApi
from .const import DEFAULT_SCAN_INTERVAL


class OpenClawCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, api: OpenClawApi) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="openclaw",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self):
        try:
            return await self.api.status()
        except Exception as err:
            raise UpdateFailed(str(err)) from err


import logging
_LOGGER = logging.getLogger(__name__)
