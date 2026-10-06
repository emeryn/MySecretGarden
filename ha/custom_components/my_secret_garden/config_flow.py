import logging
from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MySecretGardenApi, MySecretGardenAuthError, MySecretGardenConnectionError, normalize_url
from .const import CONF_API_KEY, CONF_API_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class MySecretGardenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Set up the integration from the UI."""

    VERSION = 1

    async def _test(self, url: str, api_key: str) -> str | None:
        """Return an error key, or None when the connection works."""
        api = MySecretGardenApi(async_get_clientsession(self.hass), url, api_key)
        try:
            await api.get_state()
        except MySecretGardenAuthError:
            return "invalid_auth"
        except MySecretGardenConnectionError:
            return "cannot_connect"
        except Exception:  # noqa: BLE001
            _LOGGER.exception("Unexpected error while testing My Secret Garden")
            return "unknown"
        return None

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            url = normalize_url(user_input[CONF_API_URL])
            api_key = user_input[CONF_API_KEY].strip()
            await self.async_set_unique_id(url.lower())
            self._abort_if_unique_id_configured()
            if (error := await self._test(url, api_key)) is None:
                return self.async_create_entry(title="My Secret Garden", data={CONF_API_URL: url, CONF_API_KEY: api_key})
            errors["base"] = error

        defaults = user_input or {}
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_API_URL, default=defaults.get(CONF_API_URL, "http://192.168.1.50:8000")): str,
                vol.Required(CONF_API_KEY, default=defaults.get(CONF_API_KEY, "")): str,
            }),
            errors=errors,
        )

    async def async_step_reauth(self, entry_data: Mapping[str, Any]):
        """API key missing (v1 entry), revoked or replaced on the server."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input: dict[str, Any] | None = None):
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        errors: dict[str, str] = {}
        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()
            if (error := await self._test(entry.data[CONF_API_URL], api_key)) is None:
                self.hass.config_entries.async_update_entry(entry, data={**entry.data, CONF_API_KEY: api_key})
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reauth_successful")
            errors["base"] = error

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            description_placeholders={"url": entry.data[CONF_API_URL]},
            errors=errors,
        )
