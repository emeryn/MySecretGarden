import logging

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MySecretGardenApi, MySecretGardenAuthError, MySecretGardenError
from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class MySecretGardenCoordinator(DataUpdateCoordinator[dict]):
    """Fetches the whole garden state (beds, pots, seedlings) in a single call."""

    def __init__(self, hass: HomeAssistant, api: MySecretGardenApi) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)
        self.api = api

    async def _async_update_data(self) -> dict:
        try:
            return await self.api.get_state()
        except MySecretGardenAuthError as err:
            # Starts the re-authentication flow in the Home Assistant UI
            raise ConfigEntryAuthFailed(str(err)) from err
        except MySecretGardenError as err:
            raise UpdateFailed(f"My Secret Garden API error: {err}") from err

    def items(self, kind: str) -> list[dict]:
        """Beds or pots ("bed" / "pot")."""
        return (self.data or {}).get(f"{kind}s", [])

    def item(self, kind: str, item_id) -> dict | None:
        return next((i for i in self.items(kind) if i.get("id") == item_id), None)
