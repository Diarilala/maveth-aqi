import logging
import os
from pathlib import Path

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

DAYS_BACK = 90
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
    resp.raise_for_status
    results = resp.json()
    if not results:
        raise ValueError(f"No geocoding results for query: {query}")
    lat = results[0]["lat"]
    lon = results[0]["lon"]
    return lat, lon