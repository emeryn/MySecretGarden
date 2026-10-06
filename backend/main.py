import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import auth as auth
import migration as migration
from storage import now_ms, read_json, to_int, write_json

DEFAULT_WATERING_INTERVAL = 7
SECRET_SETTINGS = ("webhook_url",)
SECRET_MASK = "********"
DEFAULT_SETTINGS = {
    "webhook_url": "", "webhook_watering_alert": True, "webhook_rain_alert": True,
    "webhook_time": "10:00", "city": "", "language": "en", "last_webhook_date": "",
}

MESSAGES = {
    "en": {
        "test": "🔔 **Connection test successful!** The My Secret Garden bot is ready.",
        "rain": "🌧️ **It's raining today, no need to water the garden!** (Watering counters reset)",
        "watering": "💦 **Watering day for: {names}**",
        "no_seedlings": "No seedlings in progress",
        "unknown": "Unknown",
    },
    "fr": {
        "test": "🔔 **Test de connexion réussi !** Le bot My Secret Garden est prêt.",
        "rain": "🌧️ **Il pleut aujourd'hui, pas besoin de passer au jardin !** (Compteurs d'arrosage réinitialisés)",
        "watering": "💦 **Jour d'arrosage pour : {names}**",
        "no_seedlings": "Aucun semis en cours",
        "unknown": "Inconnu",
    },
}


def message(settings: Dict[str, Any], key: str, **params) -> str:
    texts = MESSAGES.get(settings.get("language"), MESSAGES["en"])
    return texts[key].format(**params)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    migration.migrate_data_dir()
    auth.import_legacy_token()
    if auth.DEFAULT_CREDENTIALS:
        print("WARNING: default credentials admin / admin in use. Set APP_USERNAME and APP_PASSWORD.")
    task = asyncio.create_task(daily_check())
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)

# --- Authentication ---

PUBLIC_ROUTES = {"/api/auth/login"}
SESSION_ONLY_PREFIXES = ("/api/api-keys", "/api/auth/")


@app.middleware("http")
async def check_auth(request: Request, call_next):
    path = request.url.path
    if path.startswith("/api/") and path not in PUBLIC_ROUTES:
        header = request.headers.get("Authorization", "")
        token = header[7:] if header.startswith("Bearer ") else ""
        kind = auth.resolve(token)
        if kind is None:
            return JSONResponse({"detail": "Unauthorized"}, status_code=401)
        # An API key (Home Assistant...) cannot create other keys or act as a logged-in user
        if kind == "api_key" and path.startswith(SESSION_ONLY_PREFIXES):
            return JSONResponse({"detail": "This action requires a user session"}, status_code=403)
        request.state.token = token
    return await call_next(request)


class Credentials(BaseModel):
    username: str
    password: str


@app.post("/api/auth/login")
async def login(data: Credentials):
    if auth.check_credentials(data.username, data.password):
        return {"token": auth.create_session()}
    await asyncio.sleep(1)  # slow down password guessing
    return JSONResponse({"detail": "Invalid username or password"}, status_code=401)


@app.post("/api/auth/logout")
def logout(request: Request):
    auth.delete_session(request.state.token)
    return {"status": "ok"}


@app.get("/api/auth/me")
def me():
    return {"username": auth.USERNAME, "default_credentials": auth.DEFAULT_CREDENTIALS}


class ApiKeyRequest(BaseModel):
    name: str = ""


@app.get("/api/api-keys")
def get_api_keys():
    return auth.list_api_keys()


@app.post("/api/api-keys")
def post_api_key(data: ApiKeyRequest):
    record, key = auth.create_api_key(data.name)
    return {**record, "key": key}


@app.delete("/api/api-keys/{key_id}")
def remove_api_key(key_id: str):
    if not auth.delete_api_key(key_id):
        return JSONResponse({"detail": "API key not found"}, status_code=404)
    return {"status": "ok"}


# --- Watering logic (shared by the Discord alert and the Home Assistant routes) ---

def is_bed(plot: Dict[str, Any]) -> bool:
    return plot.get("type") == "bed"


def days_since_watering(item: Dict[str, Any], now: int) -> float:
    return (now - to_int(item.get("last_watered"), 0)) / (1000 * 3600 * 24)


def bed_interval(plantings: List[Dict[str, Any]], seeds_by_id: Dict[Any, Dict[str, Any]]) -> int:
    """Interval of the thirstiest plant in the bed (7 days when none is set)."""
    intervals = []
    for p in plantings:
        seed = seeds_by_id.get(p.get("seed_id"))
        interval = to_int((seed or {}).get("watering_interval"), 0)
        if interval > 0:
            intervals.append(interval)
    return min(intervals) if intervals else DEFAULT_WATERING_INTERVAL


def bed_needs_water(bed: Dict[str, Any], seeds_by_id: Dict[Any, Dict[str, Any]], now: int) -> bool:
    """A bed is only thirsty when something grows in it."""
    plantings = bed.get("plantings") or []
    if not is_bed(bed) or not plantings:
        return False
    return days_since_watering(bed, now) >= bed_interval(plantings, seeds_by_id)


def pot_needs_water(pot: Dict[str, Any], now: int) -> bool:
    """Same rule as the frontend: a pot without a watering interval is never thirsty."""
    interval = to_int(pot.get("watering_interval"), 0)
    return interval > 0 and days_since_watering(pot, now) >= interval


def seeds_index() -> Dict[Any, Dict[str, Any]]:
    return {s.get("id"): s for s in read_json("seeds", [])}


def load_settings() -> Dict[str, Any]:
    return {**DEFAULT_SETTINGS, **read_json("settings", {})}


# --- Garden data ---

COLLECTIONS = ("seeds", "plots", "seedlings", "pots")


def _register_collection(name: str) -> None:
    def get_items():
        return read_json(name, [])

    def put_items(data: List[Dict[str, Any]]):
        write_json(name, data)
        return {"status": "ok"}

    app.get(f"/api/{name}", name=f"get_{name}")(get_items)
    app.put(f"/api/{name}", name=f"put_{name}")(put_items)


for _name in COLLECTIONS:
    _register_collection(_name)


@app.get("/api/settings")
def get_settings():
    settings = load_settings()
    # Secrets never leave the server: the browser only receives a mask
    for key in SECRET_SETTINGS:
        if settings.get(key):
            settings[key] = SECRET_MASK
    return settings


@app.put("/api/settings")
def put_settings(data: Dict[str, Any]):
    old = load_settings()
    data["last_webhook_date"] = old.get("last_webhook_date", "")
    # Mask sent back unchanged = secret unchanged
    for key in SECRET_SETTINGS:
        if data.get(key) == SECRET_MASK:
            data[key] = old.get(key, "")
    write_json("settings", data)
    return {"status": "ok"}


@app.post("/api/import")
def import_backup(payload: Dict[str, Any]):
    """Restore a full backup (current or legacy French format)."""
    if not migration.is_backup(payload):
        return JSONResponse({"detail": "Not a My Secret Garden backup"}, status_code=400)
    data = migration.backup(payload)
    for name in COLLECTIONS:
        write_json(name, data[name])
    return {name: len(items) for name, items in data.items()}


@app.post("/api/import/seeds")
def import_seeds(items: List[Dict[str, Any]]):
    """Append a seed list (current or legacy format). Imported seeds get new ids."""
    seeds = read_json("seeds", [])
    used_ids = {s.get("id") for s in seeds}
    next_id = now_ms()
    added = 0
    for item in items:
        seed = migration.seed(item)
        while next_id in used_ids:
            next_id += 1
        seed["id"] = next_id
        used_ids.add(next_id)
        seeds.append(seed)
        added += 1
    write_json("seeds", seeds)
    return {"added": added}


# --- Home Assistant ---

@app.get("/api/ha/state")
def get_ha_state():
    """Detailed state of every bed, pot and seedling for Home Assistant."""
    now = now_ms()
    settings = load_settings()
    seeds_by_id = seeds_index()

    beds = [{
        "id": p.get("id"), "name": p.get("name") or f"Bed {p.get('id')}",
        "plant_count": sum(to_int(pl.get("quantity"), 1) for pl in p.get("plantings") or []),
        "needs_water": bed_needs_water(p, seeds_by_id, now),
        "last_watered": to_int(p.get("last_watered"), 0),
    } for p in read_json("plots", []) if is_bed(p)]

    pots = [{
        "id": p.get("id"), "name": p.get("name") or f"Pot {p.get('id')}",
        "needs_water": pot_needs_water(p, now), "environment": p.get("environment", "indoor"),
        "last_watered": to_int(p.get("last_watered"), 0),
    } for p in read_json("pots", [])]

    seedlings = read_json("seedlings", [])
    details = [
        f"{to_int(s.get('quantity'), 1)}x {(seeds_by_id.get(s.get('seed_id')) or {}).get('name') or message(settings, 'unknown')}"
        for s in seedlings
    ]
    return {
        "beds": beds,
        "pots": pots,
        "seedlings": {
            "total": sum(to_int(s.get("quantity"), 1) for s in seedlings),
            "varieties": len(seedlings),
            "details": ", ".join(details) if details else message(settings, "no_seedlings"),
        },
    }


@app.get("/api/ha/watering-status")
def get_ha_watering_status():
    """Short summary of what needs water."""
    now = now_ms()
    seeds_by_id = seeds_index()
    beds = [{"id": p.get("id"), "name": p.get("name")} for p in read_json("plots", []) if bed_needs_water(p, seeds_by_id, now)]
    pots = [{"id": p.get("id"), "name": p.get("name")} for p in read_json("pots", []) if pot_needs_water(p, now)]
    return {"total": len(beds) + len(pots), "beds": beds, "pots": pots}


@app.post("/api/ha/water")
def ha_water_all():
    """Called by Home Assistant after watering the whole garden (beds and pots)."""
    now = now_ms()
    plots = read_json("plots", [])
    pots = read_json("pots", [])
    for p in plots:
        if is_bed(p):
            p["last_watered"] = now
    for p in pots:
        p["last_watered"] = now
    write_json("plots", plots)
    write_json("pots", pots)
    return {"status": "ok"}


@app.post("/api/ha/water/{kind}/{item_id}")
def ha_water_one(kind: str, item_id: str):
    """Called by Home Assistant after watering a single bed or pot."""
    files = {"bed": "plots", "pot": "pots"}
    if kind not in files:
        return JSONResponse({"detail": "Unknown kind (expected bed or pot)"}, status_code=400)
    items = read_json(files[kind], [])
    target = next((i for i in items if str(i.get("id")) == item_id and (kind == "pot" or is_bed(i))), None)
    if target is None:
        return JSONResponse({"detail": f"{kind} {item_id} not found"}, status_code=404)
    target["last_watered"] = now_ms()
    write_json(files[kind], items)
    return {"status": "ok"}


# --- Discord notifications ---

async def send_discord(url: str, content: str) -> None:
    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json={"username": "My Secret Garden 🌻", "content": content})
        except Exception as err:
            print(f"Webhook error: {err}")


@app.post("/api/settings/test-webhook")
async def test_webhook():
    settings = load_settings()
    if not settings.get("webhook_url"):
        return JSONResponse({"detail": "No webhook URL configured"}, status_code=400)
    await send_discord(settings["webhook_url"], message(settings, "test"))
    return {"status": "ok"}


def alert_time_reached(now: datetime, configured: str) -> bool:
    """True once the configured time has passed (not only during that exact minute)."""
    try:
        alert_time = datetime.strptime(configured, "%H:%M").time()
    except (TypeError, ValueError):
        alert_time = datetime.strptime(DEFAULT_SETTINGS["webhook_time"], "%H:%M").time()
    return now.time() >= alert_time


async def rain_today(city: str) -> float:
    try:
        async with httpx.AsyncClient() as client:
            geo = await client.get("https://geocoding-api.open-meteo.com/v1/search", params={"name": city, "count": 1})
            results = geo.json().get("results")
            if results:
                forecast = await client.get("https://api.open-meteo.com/v1/forecast", params={
                    "latitude": results[0]["latitude"], "longitude": results[0]["longitude"],
                    "daily": "precipitation_sum", "timezone": "auto",
                })
                return forecast.json()["daily"]["precipitation_sum"][0] or 0
    except Exception as err:
        print("Weather error:", err)
    return 0


async def send_daily_alert(settings: Dict[str, Any]) -> None:
    rain = await rain_today(settings["city"]) if settings.get("city") else 0
    plots = read_json("plots", [])
    now = now_ms()

    if rain > 0.5:
        for p in plots:
            if is_bed(p):
                p["last_watered"] = now
        write_json("plots", plots)
        pots = read_json("pots", [])
        for p in pots:
            if p.get("environment") == "outdoor":
                p["last_watered"] = now
        write_json("pots", pots)
        if settings.get("webhook_rain_alert"):
            await send_discord(settings["webhook_url"], message(settings, "rain"))
        return

    seeds_by_id = seeds_index()
    names = {pl["name"] for p in plots if bed_needs_water(p, seeds_by_id, now) for pl in p.get("plantings") or [] if pl.get("name")}
    if names and settings.get("webhook_watering_alert"):
        await send_discord(settings["webhook_url"], message(settings, "watering", names=", ".join(sorted(names))))


async def daily_check() -> None:
    while True:
        try:
            now = datetime.now()
            settings = load_settings()
            today = now.strftime("%Y-%m-%d")
            if (settings.get("webhook_url") and settings.get("last_webhook_date") != today
                    and alert_time_reached(now, settings.get("webhook_time"))):
                await send_daily_alert(settings)
                # Re-read: the user may have changed the settings during the network calls
                settings = read_json("settings", {})
                settings["last_webhook_date"] = today
                write_json("settings", settings)
        except Exception as err:
            # Malformed data must not stop the loop for good
            print("Daily check error:", err)
        await asyncio.sleep(60)


if os.path.isdir("dist"):
    app.mount("/", StaticFiles(directory="dist", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
