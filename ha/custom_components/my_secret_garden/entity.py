from collections.abc import Callable, Iterable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEVICE_GLOBAL, DEVICE_SEEDLINGS, DOMAIN, LEGACY_PREFIX, MANUFACTURER
from .coordinator import MySecretGardenCoordinator

MODELS = {"bed": "Garden bed", "pot": "Potted plant"}


def item_key(kind: str, item_id) -> str:
    """Identifier shared by unique ids and devices, e.g. "bac_123" for a bed (v1 naming)."""
    return f"{LEGACY_PREFIX[kind]}_{item_id}"


class MySecretGardenEntity(CoordinatorEntity[MySecretGardenCoordinator]):
    """Common base: the displayed name is the device name followed by the translated entity name."""

    _attr_has_entity_name = True

    def _device(self, identifier: str, **info) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, identifier)},
            manufacturer=MANUFACTURER,
            configuration_url=self.coordinator.api.url,
            **info,
        )


class GardenEntity(MySecretGardenEntity):
    """Entity attached to the "My garden" device."""

    def __init__(self, coordinator: MySecretGardenCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_device_info = self._device(DEVICE_GLOBAL, translation_key="garden")


class SeedlingsEntity(MySecretGardenEntity):
    """Entity attached to the "Seedlings" device."""

    def __init__(self, coordinator: MySecretGardenCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_device_info = self._device(DEVICE_SEEDLINGS, translation_key="seedlings")


class ItemEntity(MySecretGardenEntity):
    """Entity attached to a bed or a pot. Becomes unavailable when the item is deleted in the app."""

    def __init__(self, coordinator: MySecretGardenCoordinator, kind: str, item: dict) -> None:
        super().__init__(coordinator)
        self.kind = kind
        self.item_id = item["id"]
        self._attr_device_info = self._device(
            item_key(kind, self.item_id),
            name=item.get("name") or f"{kind} {self.item_id}",
            model=MODELS[kind],
        )

    @property
    def item(self) -> dict | None:
        return self.coordinator.item(self.kind, self.item_id)

    @property
    def available(self) -> bool:
        return super().available and self.item is not None


@callback
def add_item_entities(
    entry: ConfigEntry,
    coordinator: MySecretGardenCoordinator,
    async_add_entities: AddEntitiesCallback,
    factory: Callable[[str, dict], Iterable[Entity]],
) -> None:
    """Create entities for existing beds/pots, then for the ones added later in the app."""
    known: set[tuple[str, object]] = set()

    @callback
    def add_new() -> None:
        new_entities: list[Entity] = []
        for kind in ("bed", "pot"):
            for item in coordinator.items(kind):
                key = (kind, item.get("id"))
                if key[1] is None or key in known:
                    continue
                known.add(key)
                new_entities.extend(factory(kind, item))
        if new_entities:
            async_add_entities(new_entities)

    add_new()
    entry.async_on_unload(coordinator.async_add_listener(add_new))
