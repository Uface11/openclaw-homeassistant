from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import OpenClawApi, OpenClawAuthError, OpenClawConnectionError, OpenClawHttpError
from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class OpenClawCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, api: OpenClawApi, *, scan_interval: int = DEFAULT_SCAN_INTERVAL) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="openclaw",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.api = api

    async def _async_update_data(self):
        try:
            return await self.api.status()
        except OpenClawAuthError as err:
            raise UpdateFailed("Authentication failed: check API token") from err
        except OpenClawConnectionError as err:
            raise UpdateFailed("Cannot reach OpenClaw Gateway") from err
        except OpenClawHttpError as err:
            raise UpdateFailed(f"Gateway API error: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected update error: {err}") from err
