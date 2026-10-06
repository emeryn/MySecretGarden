"""Minimal HTTP client for the My Secret Garden API."""
import asyncio
from typing import Any

import aiohttp

TIMEOUT = aiohttp.ClientTimeout(total=15)


class MySecretGardenError(Exception):
    """Generic API error."""


class MySecretGardenAuthError(MySecretGardenError):
    """API key rejected by the server (401)."""


class MySecretGardenConnectionError(MySecretGardenError):
    """Server unreachable or invalid response."""


def normalize_url(url: str) -> str:
    url = url.strip().rstrip("/")
    if not url.startswith(("http://", "https://")):
        url = f"http://{url}"
    return url


class MySecretGardenApi:
    def __init__(self, session: aiohttp.ClientSession, url: str, api_key: str) -> None:
        self._session = session
        self.url = normalize_url(url)
        self._api_key = api_key.strip()

    async def _request(self, method: str, path: str) -> Any:
        headers = {"Authorization": f"Bearer {self._api_key}"}
        try:
            async with self._session.request(method, f"{self.url}{path}", headers=headers, timeout=TIMEOUT) as resp:
                if resp.status == 401:
                    raise MySecretGardenAuthError("API key rejected")
                if resp.status >= 400:
                    raise MySecretGardenConnectionError(f"HTTP {resp.status} on {path}")
                return await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as err:
            raise MySecretGardenConnectionError(f"{type(err).__name__}: {err}") from err

    async def get_state(self) -> dict:
        return await self._request("GET", "/api/ha/state")

    async def water_all(self) -> None:
        await self._request("POST", "/api/ha/water")

    async def water(self, kind: str, item_id: Any) -> None:
        await self._request("POST", f"/api/ha/water/{kind}/{item_id}")
