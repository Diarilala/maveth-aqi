-- Star schema for the AQI data warehouse.

-- DIMENSION: city
-- Descriptive attributes only, no measurements.
CREATE TABLE IF NOT EXISTS dim_city (
    city_id     SERIAL PRIMARY KEY,
    city_name   VARCHAR(100) NOT NULL,
    country     VARCHAR(10)  NOT NULL,
    latitude    DOUBLE PRECISION NOT NULL,
    longitude   DOUBLE PRECISION NOT NULL,
    UNIQUE (city_name)
);

-- DIMENSION: time
-- One row per distinct hour. Descriptive/calendar attributes only.
CREATE TABLE IF NOT EXISTS dim_time (
    time_id         SERIAL PRIMARY KEY,
    timestamp_utc   TIMESTAMPTZ NOT NULL,
    date            DATE NOT NULL,
    hour            SMALLINT NOT NULL,      -- 0-23
    day_of_week     SMALLINT NOT NULL,      -- 0=Monday ... 6=Sunday
    is_weekend      BOOLEAN NOT NULL,
    month           SMALLINT NOT NULL,
    year            SMALLINT NOT NULL,
    UNIQUE (timestamp_utc)
);

-- FACT: air quality measurements
-- Numeric measures only, plus foreign keys to the dimensions.
CREATE TABLE IF NOT EXISTS fact_air_quality (
    fact_id     SERIAL PRIMARY KEY,
    city_id     INTEGER NOT NULL REFERENCES dim_city(city_id),
    time_id     INTEGER NOT NULL REFERENCES dim_time(time_id),
    aqi         SMALLINT,
    co          DOUBLE PRECISION,
    no          DOUBLE PRECISION,
    no2         DOUBLE PRECISION,
    o3          DOUBLE PRECISION,
    so2         DOUBLE PRECISION,
    pm2_5       DOUBLE PRECISION,
    pm10        DOUBLE PRECISION,
    nh3         DOUBLE PRECISION,
    UNIQUE (city_id, time_id)  -- one measurement per city per hour
);