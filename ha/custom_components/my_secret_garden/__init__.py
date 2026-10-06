"""Home Assistant integration for My Secret Garden."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MySecretGardenApi
from .const import CONF_API_KEY, CONF_API_URL, DEVICE_GLOBAL, DEVICE_SEEDLINGS, DOMAIN, LEGACY_PREFIX
from .coordinator import MySecretGardenCoordinator

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.BUTTON]

type MySecretGardenConfigEntry = ConfigEntry[MySecretGardenCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: MySecretGardenConfigEntry) -> bool:
    # Entries created with v1 have no API key: the first 401 starts the re-authentication flow
    api = MySecretGardenApi(async_get_clientsession(hass), entry.data[CONF_API_URL], entry.data.get(CONF_API_KEY, ""))
    coordinator = MySecretGardenCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: MySecretGardenConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_config_entry_device(hass: HomeAssistant, entry: MySecretGardenConfigEntry, device: dr.DeviceEntry) -> bool:
    """Allow removing a bed / pot device that no longer exists in the app."""
    coordinator = entry.runtime_data
    kinds = {prefix: kind for kind, prefix in LEGACY_PREFIX.items()}
    for domain, identifier in device.identifiers:
        if domain != DOMAIN:
            continue
        if identifier in (DEVICE_GLOBAL, DEVICE_SEEDLINGS):
            return False
        prefix, _, item_id = identifier.partition("_")
        kind = kinds.get(prefix)
        if kind and any(str(i.get("id")) == item_id for i in coordinator.items(kind)):
            return False
    return True
