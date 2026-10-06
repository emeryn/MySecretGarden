"""Conversion of the legacy French data format (v1) to the English format (v2).

Every function is idempotent: an item that is already in the v2 format is returned unchanged,
so the same code handles startup migration and the import of old or new backup files.
"""
import os
import shutil
import time
import unicodedata
from typing import Any, Dict, List, Optional

import storage as storage

SCHEMA_VERSION = 2

CATEGORIES = {
    "legume-fruit": "fruit_vegetable", "legume-racine": "root_vegetable", "legume-feuille": "leaf_vegetable",
    "fleur compagne": "companion_flower", "bulbe": "bulb", "aromatique": "herb", "cereale": "cereal",
}
SOILS = {
    "argileux (lourd)": "clay", "sableux (leger)": "sandy", "limoneux (riche)": "loamy",
    "humifere (terreau)": "humus", "calcaire": "chalky", "tout type de sol": "any",
}
MONTHS = ["janvier", "fevrier", "mars", "avril", "mai", "juin", "juillet", "aout", "septembre", "octobre", "novembre", "decembre"]
PLOT_TYPES = {"bac": "bed", "bordure": "border", "arbre": "tree", "deco": "decor"}
TREE_SIZES = {"petit": "small", "moyen": "medium", "grand": "large"}
ENVIRONMENTS = {"interieur": "indoor", "exterieur": "outdoor"}

# Legacy file name -> new file name
LEGACY_FILES = {"graines": "seeds", "parcelles": "plots", "godets": "seedlings", "pots": "pots", "reglages": "settings"}


def _norm(value: Any) -> str:
    text = unicodedata.normalize("NFD", str(value or "")).encode("ascii", "ignore").decode()
    return text.strip().lower()


def _map(value: Any, table: Dict[str, str], fallback: Optional[str] = None) -> Any:
    """Translate a legacy French label; values already in the new format pass through."""
    if value in (None, ""):
        return fallback
    if value in table.values():
        return value
    return table.get(_norm(value), value)


def _month(value: Any) -> Optional[int]:
    if value in (None, ""):
        return None
    if isinstance(value, int) and 1 <= value <= 12:
        return value
    name = _norm(value)
    return MONTHS.index(name) + 1 if name in MONTHS else None


def _pick(item: Dict[str, Any], new_key: str, old_key: str, default: Any = None) -> Any:
    if new_key in item:
        return item[new_key]
    return item.get(old_key, default)


def seed(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": item.get("id"),
        "name": _pick(item, "name", "nom", ""),
        "icon": _pick(item, "icon", "icone", "🌱"),
        "category": _map(_pick(item, "category", "type"), CATEGORIES, "fruit_vegetable"),
        "soil": _map(_pick(item, "soil", "sol"), SOILS, ""),
        "watering_interval": _pick(item, "watering_interval", "arrosage", 7),
        "in_stock": bool(_pick(item, "in_stock", "en_possession", True)),
        "is_plant": bool(_pick(item, "is_plant", "est_plant", False)),
        "expiry": _pick(item, "expiry", "peremption", "") or "",
        "tray_start": _month(_pick(item, "tray_start", "godet_debut")),
        "tray_end": _month(_pick(item, "tray_end", "godet_fin")),
        "planting_start": _month(_pick(item, "planting_start", "plantation_debut")),
        "planting_end": _month(_pick(item, "planting_end", "plantation_fin")),
        "harvest_start": _month(_pick(item, "harvest_start", "recolte_debut")),
        "harvest_end": _month(_pick(item, "harvest_end", "recolte_fin")),
    }


def planting(item: Dict[str, Any]) -> Dict[str, Any]:
    new = {
        "seed_id": _pick(item, "seed_id", "id_graine"),
        "name": _pick(item, "name", "nom", ""),
        "icon": _pick(item, "icon", "icone", "🌱"),
        "quantity": _pick(item, "quantity", "quantite", 1),
        "planted_on": _pick(item, "planted_on", "date_plantation", "") or "",
    }
    removed = _pick(item, "removed_on", "date_retrait")
    if removed:
        new["removed_on"] = removed
    return new


def plot(item: Dict[str, Any]) -> Dict[str, Any]:
    kind = _map(item.get("type") or "bac", PLOT_TYPES)
    new: Dict[str, Any] = {"id": item.get("id"), "type": kind, "name": _pick(item, "name", "nom", "") or ""}
    if kind == "border":
        for key in ("x1", "y1", "x2", "y2"):
            new[key] = item.get(key, 0)
        return new
    new["x"], new["y"] = item.get("x", 0), item.get("y", 0)
    if kind == "tree":
        new["size"] = _map(_pick(item, "size", "taille"), TREE_SIZES, "medium")
    elif kind == "decor":
        new["icon"] = _pick(item, "icon", "icone", "")
    elif kind == "bed":
        new["width"], new["height"] = item.get("width", 0), item.get("height", 0)
        new["size_x_cm"] = _pick(item, "size_x_cm", "dimX", 0)
        new["size_y_cm"] = _pick(item, "size_y_cm", "dimY", 0)
        plantings = list(_pick(item, "plantings", "plantations", None) or [])
        # Even older format: separate summer / winter lists
        plantings += (item.get("plantations_ete") or []) + (item.get("plantations_hiver") or [])
        new["plantings"] = [planting(p) for p in plantings]
        new["archive"] = [planting(p) for p in (_pick(item, "archive", "archives", None) or [])]
        new["last_watered"] = _pick(item, "last_watered", "dernier_arrosage", 0) or 0
    return new


def seedling(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": item.get("id"),
        "seed_id": _pick(item, "seed_id", "id_graine"),
        "quantity": _pick(item, "quantity", "quantite", 1),
        "location": _pick(item, "location", "emplacement", "") or "",
    }


def pot(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": item.get("id"),
        "name": _pick(item, "name", "nom", "") or "",
        "icon": _pick(item, "icon", "icone", "🪴"),
        "environment": _map(_pick(item, "environment", "environnement"), ENVIRONMENTS, "indoor"),
        "location": _pick(item, "location", "emplacement", "") or "",
        "watering_interval": _pick(item, "watering_interval", "arrosage", 7),
        "last_watered": _pick(item, "last_watered", "dernier_arrosage", 0) or 0,
    }


SETTINGS_KEYS = {
    "webhookUrl": "webhook_url", "webhookArrosage": "webhook_watering_alert", "webhookPluie": "webhook_rain_alert",
    "webhookHeure": "webhook_time", "ville": "city", "lastWebhookDate": "last_webhook_date",
}


def settings(item: Dict[str, Any]) -> Dict[str, Any]:
    new = {SETTINGS_KEYS.get(k, k): v for k, v in item.items() if k not in ("pays", "geminiKey", "geminiModel")}
    new.setdefault("language", "fr" if any(k in item for k in SETTINGS_KEYS) else "en")
    return new


def _list(items: Any, convert) -> List[Dict[str, Any]]:
    return [convert(i) for i in (items or []) if isinstance(i, dict)]


def backup(payload: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """Convert a full backup file (legacy or current) to the current format."""
    return {
        "seeds": _list(_pick(payload, "seeds", "grainotheque"), seed),
        "plots": _list(_pick(payload, "plots", "parcelles"), plot),
        "seedlings": _list(_pick(payload, "seedlings", "godets"), seedling),
        "pots": _list(payload.get("pots"), pot),
    }


def is_backup(payload: Any) -> bool:
    return isinstance(payload, dict) and any(k in payload for k in ("seeds", "plots", "grainotheque", "parcelles"))


def migrate_data_dir() -> None:
    """Convert legacy data files in place at startup. Originals are kept in data/legacy-<timestamp>/."""
    legacy = [old for old in LEGACY_FILES if storage.exists(old) and (old != "pots" or _pots_are_legacy())]
    if not legacy:
        return

    # Copy the originals first: pots.json keeps its name and is rewritten in place
    archive_dir = os.path.join(storage.DATA_DIR, f"legacy-{int(time.time())}")
    os.makedirs(archive_dir, exist_ok=True)
    for old in legacy:
        shutil.copy(storage.file_path(old), os.path.join(archive_dir, f"{old}.json"))

    converters = {"graines": seed, "parcelles": plot, "godets": seedling, "pots": pot}
    for old in legacy:
        data = storage.read_json(old, None)
        if data is None:
            continue
        converted = settings(data) if old == "reglages" else _list(data, converters[old])
        storage.write_json(LEGACY_FILES[old], converted)
        if LEGACY_FILES[old] != old:
            os.remove(storage.file_path(old))
    print(f"Legacy data migrated to the v{SCHEMA_VERSION} format, originals saved in {archive_dir}")


def _pots_are_legacy() -> bool:
    pots = storage.read_json("pots", [])
    return any(isinstance(p, dict) and ("nom" in p or "environnement" in p or "dernier_arrosage" in p) for p in pots)
