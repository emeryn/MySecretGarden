from datetime import datetime, timezone

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import MySecretGardenConfigEntry
from .entity import GardenEntity, ItemEntity, SeedlingsEntity, add_item_entities, item_key


async def async_setup_entry(hass: HomeAssistant, entry: MySecretGardenConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = entry.runtime_data
    async_add_entities([
        TotalPlantsSensor(coordinator),
        ItemsToWaterSensor(coordinator),
        SeedlingTotalSensor(coordinator),
        SeedlingVarietiesSensor(coordinator),
    ])

    def factory(kind, item):
        entities = [LastWateredSensor(coordinator, kind, item)]
        if kind == "bed":
            entities.append(BedPlantsSensor(coordinator, kind, item))
        return entities

    add_item_entities(entry, coordinator, async_add_entities, factory)


class TotalPlantsSensor(GardenEntity, SensorEntity):
    _attr_translation_key = "total_plants"
    _attr_unique_id = "msg_global_plant_count"
    _attr_native_unit_of_measurement = "plants"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int:
        return sum(b.get("plant_count", 0) for b in self.coordinator.items("bed"))


class ItemsToWaterSensor(GardenEntity, SensorEntity):
    _attr_translation_key = "items_to_water"
    _attr_unique_id = "msg_global_thirsty_count"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int:
        return sum(1 for kind in ("bed", "pot") for i in self.coordinator.items(kind) if i.get("needs_water"))


class SeedlingTotalSensor(SeedlingsEntity, SensorEntity):
    _attr_translation_key = "seedling_total"
    _attr_unique_id = "msg_godets_total"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int:
        return self.coordinator.data.get("seedlings", {}).get("total", 0)

    @property
    def extra_state_attributes(self) -> dict:
        return {"details": self.coordinator.data.get("seedlings", {}).get("details", "")}


class SeedlingVarietiesSensor(SeedlingsEntity, SensorEntity):
    _attr_translation_key = "seedling_varieties"
    _attr_unique_id = "msg_godets_varietes"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int:
        return self.coordinator.data.get("seedlings", {}).get("varieties", 0)


class BedPlantsSensor(ItemEntity, SensorEntity):
    _attr_translation_key = "plants"
    _attr_native_unit_of_measurement = "plants"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, kind, item) -> None:
        super().__init__(coordinator, kind, item)
        self._attr_unique_id = f"msg_{item_key(kind, self.item_id)}_count"

    @property
    def native_value(self) -> int | None:
        item = self.item
        return item.get("plant_count", 0) if item else None


class LastWateredSensor(ItemEntity, SensorEntity):
    _attr_translation_key = "last_watered"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator, kind, item) -> None:
        super().__init__(coordinator, kind, item)
        self._attr_unique_id = f"msg_{item_key(kind, self.item_id)}_last_watered"

    @property
    def native_value(self) -> datetime | None:
        ms = (self.item or {}).get("last_watered") or 0
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc) if ms > 0 else None
