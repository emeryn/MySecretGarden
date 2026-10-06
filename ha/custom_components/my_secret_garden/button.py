from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import MySecretGardenConfigEntry
from .api import MySecretGardenError
from .const import DOMAIN
from .entity import GardenEntity, ItemEntity, add_item_entities, item_key


async def async_setup_entry(hass: HomeAssistant, entry: MySecretGardenConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = entry.runtime_data
    async_add_entities([WaterAllButton(coordinator)])
    add_item_entities(entry, coordinator, async_add_entities, lambda kind, item: [MarkWateredButton(coordinator, kind, item)])


def _raise(err: MySecretGardenError) -> None:
    raise HomeAssistantError(translation_domain=DOMAIN, translation_key="watering_failed", translation_placeholders={"error": str(err)}) from err


class WaterAllButton(GardenEntity, ButtonEntity):
    """Tells the app the whole garden has just been watered."""

    _attr_translation_key = "water_all"
    _attr_unique_id = "msg_btn_water_global"

    async def async_press(self) -> None:
        try:
            await self.coordinator.api.water_all()
        except MySecretGardenError as err:
            _raise(err)
        await self.coordinator.async_request_refresh()


class MarkWateredButton(ItemEntity, ButtonEntity):
    """Tells the app this bed / pot has just been watered."""

    _attr_translation_key = "mark_watered"

    def __init__(self, coordinator, kind, item) -> None:
        super().__init__(coordinator, kind, item)
        self._attr_unique_id = f"msg_btn_water_{item_key(kind, self.item_id)}"

    async def async_press(self) -> None:
        try:
            await self.coordinator.api.water(self.kind, self.item_id)
        except MySecretGardenError as err:
            _raise(err)
        await self.coordinator.async_request_refresh()
