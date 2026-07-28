from datetime import datetime, timezone
import json
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
RAW_DIR = PROJECT_DIR / "raw"
CLEAN_DIR = PROJECT_DIR / "clean"
CLEAN_FILE = CLEAN_DIR / "air_quality.csv"

# City coordinates, defined once here instead of trusting each raw file,
# so every row uses the exact same lat/lon for a given city.
CITIES_COORDS = {
    "hanoi": {"lat": 21.0285, "lon": 105.8048, "country": "VN"},
    "manila": {"lat": 14.6534, "lon": 120.9986, "country": "PH"},
    "taipei": {"lat": 25.0330, "lon": 121.5607, "country": "TW"},
    "tunis": {"lat": 36.8065, "lon": 10.1815, "country": "TN"},
    "vancouver": {"lat": 49.2827, "lon": -123.1207, "country": "CA"},
}
 
 
def parse_city_file(city_slug: str, file_path: Path) -> list[dict]:
    """
    Open one raw JSON file and return a list of rows (dicts),
    one per reading found in the "list" field.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
 
    coords = CITIES_COORDS.get(city_slug)
    rows = []
 
    for entry in data.get("list", []):
        # OpenWeatherMap gives a Unix timestamp, convert it to a readable UTC datetime
        dt_unix = entry["dt"]
        dt_utc = datetime.fromtimestamp(dt_unix, tz=timezone.utc)
 
        components = entry.get("components", {})
 
        row = {
            "city": city_slug,
            "country": coords["country"] if coords else None,
            "latitude": coords["lat"] if coords else None,
            "longitude": coords["lon"] if coords else None,
            "timestamp_utc": dt_utc.isoformat(),
            "aqi": entry.get("main", {}).get("aqi"),
            "co": components.get("co"),
            "no": components.get("no"),
            "no2": components.get("no2"),
            "o3": components.get("o3"),
            "so2": components.get("so2"),
            "pm2_5": components.get("pm2_5"),
            "pm10": components.get("pm10"),
            "nh3": components.get("nh3"),
        }
        rows.append(row)
 
    return rows
 
 
def main():
    all_rows = []
 
    # RAW_DIR contains one subfolder per city: raw/hanoi/, raw/manila/, etc.
    for city_dir in sorted(RAW_DIR.iterdir()):
        if not city_dir.is_dir():
            continue
 
        city_slug = city_dir.name
        json_files = sorted(city_dir.glob("*.json"))
        print(f"{city_slug}: {len(json_files)} file(s) found")
 
        for file_path in json_files:
            try:
                rows = parse_city_file(city_slug, file_path)
                all_rows.extend(rows)
            except Exception as e:
                # Don't let one broken file stop the whole run
                print(f"  Error reading {file_path.name}: {e}")
 
    if not all_rows:
        print("No data found in raw/. Nothing to write.")
        return
 
    df = pd.DataFrame(all_rows)
 
    # Deduplicate: same city + same hour should appear only once.
    # "keep=last" favors the most recently written file in case of overlap
    # between backfill.py and collect.py.
    before = len(df)
    df = df.drop_duplicates(subset=["city", "timestamp_utc"], keep="last")
    after = len(df)
    print(f"Duplicates removed: {before - after} (same city + same hour)")
 
    df = df.sort_values(by=["city", "timestamp_utc"]).reset_index(drop=True)
 
    CLEAN_DIR.mkdir(exist_ok=True)
    df.to_csv(CLEAN_FILE, index=False)
 
    print(f"\n{len(df)} rows written to {CLEAN_FILE}")
    print(f"Cities present: {sorted(df['city'].unique())}")
    print(f"Date range covered: {df['timestamp_utc'].min()} -> {df['timestamp_utc'].max()}")
 
 
if __name__ == "__main__":
    main()