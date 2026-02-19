import asyncio
import json
import os
import time
from datetime import datetime
import httpx
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles 
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def get_file_path(name: str):
    return os.path.join(DATA_DIR, f"{name}.json")

def read_json(name: str, default: Any):
    path = get_file_path(name)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return default
    return default

def write_json(name: str, data: Any):
    with open(get_file_path(name), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.get("/api/graines")
def get_graines(): return read_json("graines", [])

@app.post("/api/graines")
def save_graines(data: List[Dict[str, Any]]):
    write_json("graines", data)
    return {"status": "ok"}

@app.get("/api/parcelles")
def get_parcelles(): return read_json("parcelles", [])

@app.post("/api/parcelles")
def save_parcelles(data: List[Dict[str, Any]]):
    write_json("parcelles", data)
    return {"status": "ok"}

@app.get("/api/godets")
def get_godets(): return read_json("godets", [])

@app.post("/api/godets")
def save_godets(data: List[Dict[str, Any]]):
    write_json("godets", data)
    return {"status": "ok"}

@app.get("/api/reglages")
def get_reglages():
    return read_json("reglages", {
        "webhookUrl": "", "webhookArrosage": True, "webhookPluie": True, 
        "webhookHeure": "10:00", "ville": "", "pays": "", "lastWebhookDate": "",
        "geminiKey": "", "geminiModel": "" 
    })

@app.post("/api/reglages")
def save_reglages(data: Dict[str, Any]):
    old_reglages = read_json("reglages", {})
    data["lastWebhookDate"] = old_reglages.get("lastWebhookDate", "")
    write_json("reglages", data)
    return {"status": "ok"}

async def envoyer_discord(url: str, message: str):
    async with httpx.AsyncClient() as client:
        payload = {"username": "My Secret Garden 🌻", "content": message}
        try:
            await client.post(url, json=payload)
        except Exception as e:
            print(f"Erreur webhook: {e}")

@app.post("/api/test-webhook")
async def test_webhook():
    reglages = read_json("reglages", {})
    url = reglages.get("webhookUrl")
    if not url: return {"error": "No URL configured"}
    await envoyer_discord(url, "🔔 **Test de connexion réussi !** Le bot My Secret Garden est prêt.")
    return {"status": "ok"}

async def verification_quotidienne():
    while True:
        now = datetime.now()
        reglages = read_json("reglages", {})
        
        url = reglages.get("webhookUrl")
        heure_config = reglages.get("webhookHeure", "10:00")
        
        if url and f"{now.hour:02d}:{now.minute:02d}" == heure_config:
            last_sent = reglages.get("lastWebhookDate")
            today_str = now.strftime("%Y-%m-%d")
            
            if last_sent != today_str:
                pluie_aujourdhui = 0
                ville = reglages.get("ville", "")
                if ville:
                    try:
                        async with httpx.AsyncClient() as client:
                            geo = await client.get(f"https://geocoding-api.open-meteo.com/v1/search?name={ville}&count=1")
                            if geo.json().get("results"):
                                lat, lon = geo.json()["results"][0]["latitude"], geo.json()["results"][0]["longitude"]
                                meteo = await client.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_sum&timezone=auto")
                                pluie_aujourdhui = meteo.json()["daily"]["precipitation_sum"][0]
                    except Exception as e:
                        print("Erreur météo:", e)

                parcelles = read_json("parcelles", [])
                graines = read_json("graines", [])
                saison = "plantations_ete" if now.month >= 4 and now.month <= 9 else "plantations_hiver"
                
                plantes_a_arroser = set()
                
                if pluie_aujourdhui > 0.5:
                    for p in parcelles:
                        p["dernier_arrosage"] = int(time.time() * 1000)
                    write_json("parcelles", parcelles)
                    if reglages.get("webhookPluie"):
                        await envoyer_discord(url, "🌧️ **Il pleut aujourd'hui, coup de bol pas besoin de passer au jardin !** (Compteurs d'arrosage réinitialisés)")
                else:
                    for p in parcelles:
                        plantes_bac = p.get(saison, [])
                        if not plantes_bac: continue
                        
                        min_freq = 7 
                        for pl in plantes_bac:
                            gr = next((g for g in graines if g.get("id") == pl.get("id_graine")), None)
                            if gr and gr.get("arrosage"):
                                min_freq = min(min_freq, int(gr["arrosage"]))
                        
                        dernier = p.get("dernier_arrosage", 0)
                        jours_depuis = (int(time.time() * 1000) - dernier) / (1000 * 3600 * 24)
                        
                        if jours_depuis >= min_freq:
                            for pl in plantes_bac:
                                plantes_a_arroser.add(pl["nom"])
                    
                    if plantes_a_arroser and reglages.get("webhookArrosage"):
                        noms = ", ".join(plantes_a_arroser)
                        await envoyer_discord(url, f"💦 **Jour d'arrosage pour : {noms}**")
                
                reglages["lastWebhookDate"] = today_str
                write_json("reglages", reglages)

        await asyncio.sleep(60)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(verification_quotidienne())

if os.path.isdir("dist"):
    app.mount("/", StaticFiles(directory="dist", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)