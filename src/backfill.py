from datetime import datetime, timedelta, timezone
import json
import logging
import os
from pathlib import Path
import time

from dotenv import load_dotenv
import requests


load_dotenv()

API_KEY = os.environ["OPENWEATHER_API_KEY"]
GEOCODE_URL = os.environ["GEOCODE_URL"]
AIR_POLLUTION_HISTORY_URL = os.environ["AIR_POLLUTION_HISTORY_URL"]

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
RAW_DIR = PROJECT_ROOT / 'raw'

CITIES = [
    {"name": "Hanoi", "q": "Hanoi,VN"},
    {"name": "Manila", "q": "Manila,PH"},
    {"name": "Taipei", "q": "Taipei,TW"},
    {"name": "Tunis", "q": "Tunis,TN"},
    {"name": "Vancouver", "q": "Vancouver,CA"},
]

DAYS_BACK = 365
CHUNK_DAYS = 20
REQUEST_PAUSE_SECONDS = 1

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

def slugify(name: str) -> str:
    return name.strip().lower().replace(" ", "_")

def geocode(query: str) -> tuple[float, float]:
    resp = requests.get(
        GEOCODE_URL,
        params={"q": query, "limit": 1, "appid": API_KEY},
        timeout=15,
    )
    resp.raise_for_status()
    results = resp.json()
    if not results:
        raise ValueError(f"No geocoding results for query: {query}")
    lat = results[0]["lat"]
    lon = results[0]["lon"]
    return lat, lon

def fetch_aqi_window(lat: float, lon: float, start: datetime, end: datetime) -> dict:
    resp = requests.get(
        AIR_POLLUTION_HISTORY_URL,
        params={
            "lat": lat,
            "lon": lon,
            "start": int(start.timestamp()),
            "end": int(end.timestamp()),
            "appid": API_KEY,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()

def date_windows(days_back: int, chunk_days: int):
    now = datetime.now(timezone.utc)
    range_start = now - timedelta(days=days_back)

    cursor = range_start
    while cursor < now:
        window_end = min(cursor + timedelta(days=chunk_days), now)
        yield cursor, window_end
        cursor = window_end

def backfill_city(city_name: str, query: str, days_back: int, chunk_days: int) -> None:
    slug = slugify(city_name)
    city_dir = RAW_DIR / slug
    city_dir.mkdir(parents=True, exist_ok=True)
    lat, lon = geocode(query)
    log.info(f"{city_name}: resolved to lat={lat}, lon={lon}")

    for start, end in date_windows(days_back, chunk_days):
        fname = f"{start.date().isoformat()}_{end.date().isoformat()}.json"
        out_path = city_dir / fname
        if out_path.exists():
            log.info(f"{city_name}: {fname} already exists, skipping")
            continue
        try:
            data = fetch_aqi_window(lat, lon, start, end)
        except requests.HTTPError as e:
            log.error(f"{city_name} {fname}: HTTP error {e.response.status_code} - {e}")
            continue
        except Exception as e:
            log.error(f"{city_name} {fname}: unexpected error - {e}")
            continue

        out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        n_readings = len(data.get("list", []))
        log.info(f"{city_name} {fname}: saved ({n_readings} hourly readings)")
        time.sleep(REQUEST_PAUSE_SECONDS)

def main():
    RAW_DIR.mkdir(exist_ok=True)
    for city in CITIES:
        backfill_city(city["name"], city["q"], DAYS_BACK, CHUNK_DAYS)
    log.info("Backfill complete.")

if __name__ == "__main__":
    main()