import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

API_KEY = os.environ["OPENWEATHER_API_KEY"]
GEOCODE_URL = os.environ["GEOCODE_URL"]
AIR_POLLUTION_HISTORY_URL = os.environ["AIR_POLLUTION_HISTORY_URL"]

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
RAW_DIR = PROJECT_ROOT / 'raw'