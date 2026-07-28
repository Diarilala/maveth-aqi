from datetime import datetime, timezone
import json
import os
from pathlib import Path

import requests


CITIES = [
    {"name": "Hanoi", "lat": 21.0285, "lon": 105.8048},
    {"name": "Manila", "lat": 14.6534, "lon": 120.9986},
    {"name": "Taipei", "lat": 25.0330, "lon": 121.5607},
    {"name": "Tunis", "lat": 36.8065, "lon": 10.1815},
    {"name": "Vancouver", "lat": 49.2827, "lon": -123.1207},
]

AIR_POLLUTION_URL = "http://api.openweathermap.org/data/2.5/air_pollution"
RAW_DIR = Path(__file__).parent.parent / 'raw'

def slugify(name: str) -> str:
    return name.strip().lower().replace(" ", "_")

def fetch_current_aqi(lat: float, lon: float, api_key: str) -> dict:
    resp = requests.get(
        AIR_POLLUTION_URL,
        params={"lat": lat, "lon": lon, "appid": api_key},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()

def main():
    api_key = os.environ["OPENWEATHER_API_KEY"]
    run_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")

    for city in CITIES:
        slug = slugify(city["name"])
        city_dir = RAW_DIR / slug
        city_dir.mkdir(parents=True, exist_ok=True)

        data = fetch_current_aqi(city["lat"], city["lon"], api_key)

        out_path = city_dir / f"{run_ts}.json"
        out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        print(f"{city['name']}: saved {out_path}")

if __name__ == "__main__":
    main()        