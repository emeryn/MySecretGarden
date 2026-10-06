# 🌻 My Secret Garden - Home Assistant integration

This integration connects your **My Secret Garden** app to Home Assistant. Home Assistant then knows the watering needs of every growing bed and potted plant, and can automate watering (valves, pumps, notifications...).

Entity names are available in **English** and **French**, following the language of Home Assistant.

## ✨ Features

A **device** is created for every growing bed and potted plant of the app. Beds and pots added later in the app appear automatically.

| Device | Entity | Purpose |
|---|---|---|
| Every bed / pot | `binary_sensor` **Needs water** | On when the item is thirsty (watering interval of its thirstiest plant) |
| | `button` **Mark as watered** | Tells the app the item has just been watered |
| | `sensor` **Last watered** | Date of the last watering |
| Every bed | `sensor` **Plants** | Number of plants in the bed |
| My garden | `binary_sensor` **Watering alert** | On when at least one bed or pot is thirsty. Attributes `beds_to_water` and `pots_to_water` |
| | `sensor` **Items to water** / **Total plants** | Global counters |
| | `button` **Water everything** | Records a watering of the whole garden |
| Seedlings | `sensor` **Seedling trays** / **Varieties sown** | Seedling follow-up |

Data is refreshed every 15 minutes, and right after a button press.

## ⚠️ Requirements

* Home Assistant **2024.6** or later.
* The **My Secret Garden** server (version 2 or later) reachable from Home Assistant (e.g. `http://192.168.1.50:8000`).
* An **API key**, created in the app under **Settings → API keys** (or in one click from the **Home Assistant** tab).

## 📥 Installation

### With HACS (recommended)

1. Open **HACS** in Home Assistant.
2. ⋮ menu (top right) > **Custom repositories**.
3. Add the URL of this repository with the **Integration** category.
4. Download **My Secret Garden**, then **restart Home Assistant**.

### Manually

Copy the `custom_components/my_secret_garden` folder into the `config/custom_components/` folder of Home Assistant, then restart.

## ⚙️ Configuration

1. **Settings** > **Devices & services** > **+ Add integration**.
2. Search for **My Secret Garden**.
3. Enter the server URL (with the port) and the API key. The connection is tested before the integration is created.

If the key is revoked, Home Assistant shows a **"Re-authentication required"** notification: paste a new key there.

## 🤖 Automation example

Water a bed every evening when it is thirsty, then tell the app. Entity ids follow the name of the bed (here "North bed") and the language of Home Assistant:

```yaml
alias: "Automatic watering: North bed"
trigger:
  - platform: time
    at: "21:00:00"
condition:
  - condition: state
    entity_id: binary_sensor.north_bed_needs_water
    state: "on"
action:
  - service: switch.turn_on
    target:
      entity_id: switch.valve_north_bed
  - delay: "00:10:00"
  - service: switch.turn_off
    target:
      entity_id: switch.valve_north_bed
  - service: button.press
    target:
      entity_id: button.north_bed_mark_as_watered
```

The **Home Assistant** tab of the app generates these examples with the names of your own beds.

## 🔄 Upgrading from 1.x

Version 2.0 requires My Secret Garden 2 (English API, API keys). After the update, Home Assistant asks for an API key through a re-authentication notification. Existing entities and their ids are kept.
