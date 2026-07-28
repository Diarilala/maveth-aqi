import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


load_dotenv()

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLEAN_FILE = PROJECT_ROOT / "clean" / "air_quality.csv"
CONNECTION_STRING = os.environ["NEON_CONNECTION_STRING"]

# Each dimension is described once here: which columns it has and which
# column must stay unique. bulk_upsert() below uses this to avoid repeating
# the same insert/staging logic twice.
DIM_CITY_COLUMNS = ["city_name", "country", "latitude", "longitude"]
DIM_TIME_COLUMNS = ["timestamp_utc", "date", "hour", "day_of_week", "is_weekend", "month", "year"]
FACT_COLUMNS = ["city_id", "time_id", "aqi", "co", "no", "no2", "o3", "so2", "pm2_5", "pm10", "nh3"]


# Building the dimension tables from the clean CSV
def build_dim_city(df: pd.DataFrame) -> pd.DataFrame:
    """One row per distinct city, with its descriptive attributes only."""
    return (
        df[["city", "country", "latitude", "longitude"]]
        .drop_duplicates(subset=["city"])
        .rename(columns={"city": "city_name"})
        .reset_index(drop=True)
    )


def build_dim_time(df: pd.DataFrame) -> pd.DataFrame:
    """One row per distinct timestamp, with calendar attributes computed from it."""
    timestamps = pd.to_datetime(df["timestamp_utc"].unique(), utc=True)
    dim_time = pd.DataFrame({"timestamp_utc": timestamps})

    dim_time["date"] = dim_time["timestamp_utc"].dt.date
    dim_time["hour"] = dim_time["timestamp_utc"].dt.hour
    dim_time["day_of_week"] = dim_time["timestamp_utc"].dt.dayofweek  # 0=Monday
    dim_time["is_weekend"] = dim_time["day_of_week"].isin([5, 6])
    dim_time["month"] = dim_time["timestamp_utc"].dt.month
    dim_time["year"] = dim_time["timestamp_utc"].dt.year

    return dim_time.sort_values("timestamp_utc").reset_index(drop=True)


# Generic bulk loading helper, shared by both dimensions
def bulk_upsert(engine: Engine, df: pd.DataFrame, table_name: str,
                 columns: list[str], conflict_col: str) -> None:
    """
    Load a DataFrame into `table_name` without duplicates, using a temporary
    staging table + a single INSERT ... SELECT ... ON CONFLICT.
    Much faster than inserting row by row.
    """
    staging_table = f"staging_{table_name}"
    cols_sql = ", ".join(columns)

    with engine.begin() as conn:
        df.to_sql(staging_table, conn, if_exists="replace", index=False)
        conn.execute(text(f"""
            INSERT INTO {table_name} ({cols_sql})
            SELECT {cols_sql} FROM {staging_table}
            ON CONFLICT ({conflict_col}) DO NOTHING
        """))
        conn.execute(text(f"DROP TABLE {staging_table}"))


def fetch_dimension_ids(engine: Engine) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Read back the auto-generated ids, needed to build the fact table."""
    with engine.begin() as conn:
        city_ids = pd.read_sql("SELECT city_id, city_name FROM dim_city", conn)
        time_ids = pd.read_sql("SELECT time_id, timestamp_utc FROM dim_time", conn)

    time_ids["timestamp_utc"] = pd.to_datetime(time_ids["timestamp_utc"], utc=True)
    return city_ids, time_ids


# Building and loading the fact table
def build_fact_table(df: pd.DataFrame, city_ids: pd.DataFrame, time_ids: pd.DataFrame) -> pd.DataFrame:
    """Attach city_id / time_id foreign keys to each measurement row."""
    fact_df = df.merge(
        city_ids, left_on="city", right_on="city_name", how="left"
    ).merge(
        time_ids, left_on="timestamp_utc", right_on="timestamp_utc", how="left"
    )[FACT_COLUMNS]

    missing = fact_df[["city_id", "time_id"]].isna().any(axis=1).sum()
    if missing:
        print(f"Warning: {missing} rows could not be matched to a city_id/time_id and will be skipped")
        fact_df = fact_df.dropna(subset=["city_id", "time_id"])

    return fact_df


def load_fact_table(engine: Engine, fact_df: pd.DataFrame) -> None:
    """Replace the whole fact table content, so re-running never duplicates rows."""
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE fact_air_quality"))
        fact_df.to_sql("fact_air_quality", conn, if_exists="append", index=False)


# main
def main():
    print(f"Reading {CLEAN_FILE} ...")
    df = pd.read_csv(CLEAN_FILE, parse_dates=["timestamp_utc"])

    engine = create_engine(CONNECTION_STRING)

    dim_city = build_dim_city(df)
    print("Loading dim_city ...")
    bulk_upsert(engine, dim_city, "dim_city", DIM_CITY_COLUMNS, conflict_col="city_name")
    print(f"dim_city: {len(dim_city)} cities processed")

    dim_time = build_dim_time(df)
    print("Loading dim_time (this is the big one, may take a bit) ...")
    bulk_upsert(engine, dim_time, "dim_time", DIM_TIME_COLUMNS, conflict_col="timestamp_utc")
    print(f"dim_time: {len(dim_time)} timestamps processed")

    city_ids, time_ids = fetch_dimension_ids(engine)
    fact_df = build_fact_table(df, city_ids, time_ids)

    print("Loading fact_air_quality (bulk insert) ...")
    load_fact_table(engine, fact_df)
    print(f"fact_air_quality: {len(fact_df)} rows loaded")

    print("\nWarehouse load complete.")


if __name__ == "__main__":
    main()