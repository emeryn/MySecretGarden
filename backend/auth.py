"""Authentication: username / password login sessions and long-lived API keys.

Tokens are never stored in clear text, only their SHA-256 hash (data/auth.json).
"""
import hashlib
import hmac
import os
import secrets
import threading
from typing import Any, Dict, List, Optional, Tuple

import storage as storage

USERNAME = os.environ.get("APP_USERNAME") or "admin"
PASSWORD = os.environ.get("APP_PASSWORD") or "admin"
DEFAULT_CREDENTIALS = USERNAME == "admin" and PASSWORD == "admin"

SESSION_TTL_MS = 30 * 24 * 3600 * 1000   # sliding expiry: 30 days without activity
TOUCH_INTERVAL_MS = 60 * 1000            # do not rewrite auth.json on every request
API_KEY_PREFIX = "msg_"

_lock = threading.Lock()


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _load() -> Dict[str, Any]:
    data = storage.read_json("auth", {})
    data.setdefault("sessions", {})
    data.setdefault("api_keys", [])
    return data


def _save(data: Dict[str, Any]) -> None:
    storage.write_json("auth", data)


def same_secret(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def check_credentials(username: str, password: str) -> bool:
    # Evaluate both comparisons to keep the timing independent of which one fails
    user_ok = same_secret(username, USERNAME)
    password_ok = same_secret(password, PASSWORD)
    return user_ok and password_ok


def create_session() -> str:
    token = secrets.token_urlsafe(32)
    now = storage.now_ms()
    with _lock:
        data = _load()
        # Drop expired sessions while we are writing anyway
        data["sessions"] = {h: s for h, s in data["sessions"].items() if now - s.get("last_used", 0) < SESSION_TTL_MS}
        data["sessions"][_hash(token)] = {"created": now, "last_used": now}
        _save(data)
    return token


def delete_session(token: str) -> None:
    with _lock:
        data = _load()
        if data["sessions"].pop(_hash(token), None) is not None:
            _save(data)


def resolve(token: str) -> Optional[str]:
    """Return "session", "api_key" or None for an unknown / expired token."""
    if not token:
        return None
    digest = _hash(token)
    now = storage.now_ms()
    with _lock:
        data = _load()
        session = data["sessions"].get(digest)
        if session is not None:
            if now - session.get("last_used", 0) >= SESSION_TTL_MS:
                del data["sessions"][digest]
                _save(data)
                return None
            if now - session.get("last_used", 0) > TOUCH_INTERVAL_MS:
                session["last_used"] = now
                _save(data)
            return "session"
        for key in data["api_keys"]:
            if same_secret(key["hash"], digest):
                if now - (key.get("last_used_at") or 0) > TOUCH_INTERVAL_MS:
                    key["last_used_at"] = now
                    _save(data)
                return "api_key"
    return None


def _public(key: Dict[str, Any]) -> Dict[str, Any]:
    return {k: key.get(k) for k in ("id", "name", "prefix", "created_at", "last_used_at")}


def list_api_keys() -> List[Dict[str, Any]]:
    return [_public(k) for k in _load()["api_keys"]]


def create_api_key(name: str) -> Tuple[Dict[str, Any], str]:
    """Create a key and return (public record, clear key). The clear key is shown once only."""
    key = API_KEY_PREFIX + secrets.token_urlsafe(32)
    record = {
        "id": secrets.token_hex(8),
        "name": (name or "").strip()[:60] or "API key",
        "prefix": key[:len(API_KEY_PREFIX) + 6],
        "hash": _hash(key),
        "created_at": storage.now_ms(),
        "last_used_at": None,
    }
    with _lock:
        data = _load()
        data["api_keys"].append(record)
        _save(data)
    return _public(record), key


def delete_api_key(key_id: str) -> bool:
    with _lock:
        data = _load()
        kept = [k for k in data["api_keys"] if k["id"] != key_id]
        if len(kept) == len(data["api_keys"]):
            return False
        data["api_keys"] = kept
        _save(data)
    return True


def import_legacy_token() -> None:
    """v1 used a single token in data/api_token: keep it working as an API key so Home Assistant is not cut off."""
    path = os.path.join(storage.DATA_DIR, "api_token")
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        token = f.read().strip()
    if token:
        with _lock:
            data = _load()
            if not any(k["hash"] == _hash(token) for k in data["api_keys"]):
                data["api_keys"].append({
                    "id": secrets.token_hex(8), "name": "Legacy token", "prefix": token[:6],
                    "hash": _hash(token), "created_at": storage.now_ms(), "last_used_at": None,
                })
                _save(data)
    os.remove(path)
    print("Legacy data/api_token imported as the API key 'Legacy token'")
