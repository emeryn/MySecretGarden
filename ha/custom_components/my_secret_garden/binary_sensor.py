from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import MySecretGardenConfigEntry
from .entity import GardenEntity, ItemEntity, add_item_entities, item_key


async def async_setup_entry(hass: HomeAssistant, entry: MySecretGardenConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = entry.runtime_data
    async_add_entities([WateringAlertSensor(coordinator)])
    add_item_entities(entry, coordinator, async_add_entities, lambda kind, item: [NeedsWaterSensor(coordinator, kind, item)])


class WateringAlertSensor(GardenEntity, BinarySensorEntity):
    """On as soon as at least one bed or pot is thirsty."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_translation_key = "watering_alert"
    _attr_unique_id = "msg_global_water_alert"

    def _thirsty(self, kind: str) -> list[str]:
        return [i.get("name") for i in self.coordinator.items(kind) if i.get("needs_water")]

    @property
    def is_on(self) -> bool:
        return bool(self._thirsty("bed") or self._thirsty("pot"))

    @property
    def extra_state_attributes(self) -> dict:
        return {"beds_to_water": self._thirsty("bed"), "pots_to_water": self._thirsty("pot")}


class NeedsWaterSensor(ItemEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_translation_key = "needs_water"

    def __init__(self, coordinator, kind, item) -> None:
        super().__init__(coordinator, kind, item)
        self._attr_unique_id = f"msg_{item_key(kind, self.item_id)}_water"

    @property
    def is_on(self) -> bool | None:
        item = self.item
        return bool(item.get("needs_water")) if item else None
