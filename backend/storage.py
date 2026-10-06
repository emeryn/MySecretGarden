"""JSON file storage in the data directory."""
import json
import os
import shutil
import tempfile
import time
from typing import Any

DATA_DIR = os.environ.get("DATA_DIR", "data")
os.makedirs(DATA_DIR, exist_ok=True)


def file_path(name: str) -> str:
    return os.path.join(DATA_DIR, f"{name}.json")


def exists(name: str) -> bool:
    return os.path.exists(file_path(name))


def read_json(name: str, default: Any) -> Any:
    path = file_path(name)
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as err:
            # Keep a copy of the damaged file so the next save does not silently erase it
            backup = f"{path}.corrupt-{int(time.time())}"
            shutil.copy(path, backup)
            print(f"Could not read {path} ({err}), copy saved to {backup}")
            return default


def write_json(name: str, data: Any) -> None:
    # Atomic write: temporary file then rename, so a crash never leaves a half-written JSON file
    fd, tmp_path = tempfile.mkstemp(dir=DATA_DIR, prefix=f".{name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, file_path(name))
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def now_ms() -> int:
    return int(time.time() * 1000)


def to_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
