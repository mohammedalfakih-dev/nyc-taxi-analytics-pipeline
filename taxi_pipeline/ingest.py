"""Load local fixtures or one TLC month, with transactional monthly replacement."""

import argparse
import io
import re
from contextlib import closing

import pandas as pd
import psycopg2
import requests
from psycopg2 import sql
from psycopg2.extras import execute_values

from taxi_pipeline.config import ROOT, database_url, raw_schema, schema_name

TLC_BASE = "https://d37ci6vzurychx.cloudfront.net"
TRIP_COLUMNS = [
    "vendor_id",
    "pickup_datetime",
    "dropoff_datetime",
    "pickup_location_id",
    "dropoff_location_id",
    "passenger_count",
    "trip_distance",
    "fare_amount",
    "tip_amount",
    "total_amount",
    "payment_type",
]
INT_COLUMNS = [
    "vendor_id",
    "pickup_location_id",
    "dropoff_location_id",
    "passenger_count",
    "payment_type",
]


def month_bounds(month: str) -> tuple[pd.Timestamp, pd.Timestamp]:
    if not re.fullmatch(r"\d{4}-\d{2}", month):
        raise ValueError("Month must be YYYY-MM")
    start = pd.Timestamp(f"{month}-01")
    return start, start + pd.DateOffset(months=1)


def prepare_month(frame: pd.DataFrame, month: str) -> pd.DataFrame:
    """Preserve source-row positions; filter pickup timestamps to the requested month."""
    start, end = month_bounds(month)
    missing = set(TRIP_COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError(f"Input is missing columns: {sorted(missing)}")
    frame = frame.copy()
    if "source_row_number" not in frame:
        frame["source_row_number"] = range(1, len(frame) + 1)
    for name in ["pickup_datetime", "dropoff_datetime"]:
        frame[name] = pd.to_datetime(frame[name], errors="coerce")
        if frame[name].dt.tz is not None:
            raise ValueError("TLC timestamps must be timezone-naive local timestamps")
    frame = frame[(frame.pickup_datetime >= start) & (frame.pickup_datetime < end)].copy()
    if frame.empty:
        raise ValueError(f"No trips with pickup timestamps in {month}; refusing replacement")
    for name in INT_COLUMNS:
        frame[name] = pd.to_numeric(frame[name], errors="coerce").astype("Int64")
    for name in ["trip_distance", "fare_amount", "tip_amount", "total_amount"]:
        frame[name] = pd.to_numeric(frame[name], errors="coerce")
    frame["source_month"] = start.date()
    return frame[["source_month", "source_row_number", *TRIP_COLUMNS]]


def normalize_zones(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.rename(
        columns={"LocationID": "location_id", "Borough": "borough", "Zone": "zone"}
    )
    frame = frame[["location_id", "borough", "zone", "service_zone"]].copy()
    frame["location_id"] = pd.to_numeric(frame["location_id"], errors="raise").astype(int)
    if frame.location_id.duplicated().any():
        raise ValueError("Zone location IDs must be unique")
    for name in ["borough", "zone", "service_zone"]:
        frame[name] = frame[name].fillna("Unknown")
    return frame


def rows(frame: pd.DataFrame) -> list[tuple]:
    """Convert pandas missing values and scalar types to database-ready values."""
    cleaned = frame.astype(object).where(pd.notna(frame), None)
    return list(cleaned.itertuples(index=False, name=None))


def replace_month(
    frame: pd.DataFrame,
    zones: pd.DataFrame,
    month: str,
    url=None,
    schema=None,
    source_kind="sample",
) -> int:
    """Replace exactly one month and upsert zone references in one transaction."""
    schema = schema_name(schema or raw_schema())
    start, end = month_bounds(month)
    prepared = prepare_month(frame, month)
    prepared["source_kind"] = source_kind
    zones = normalize_zones(zones)
    with closing(psycopg2.connect(url or database_url())) as connection, connection:
        with connection.cursor() as cursor:
            # Serialize loaders sharing this raw schema, including zone updates.
            cursor.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (schema,))
            cursor.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(schema)))
            cursor.execute(
                sql.SQL("""
                CREATE TABLE IF NOT EXISTS {}.raw_zones (
                    location_id integer PRIMARY KEY, borough text NOT NULL,
                    zone text NOT NULL, service_zone text NOT NULL
                )
            """).format(sql.Identifier(schema))
            )
            cursor.execute(
                sql.SQL("""
                CREATE TABLE IF NOT EXISTS {}.raw_trips (
                    source_month date NOT NULL, source_row_number bigint NOT NULL,
                    vendor_id integer, pickup_datetime timestamp, dropoff_datetime timestamp,
                    pickup_location_id integer, dropoff_location_id integer,
                    passenger_count integer, trip_distance double precision,
                    fare_amount double precision, tip_amount double precision,
                    total_amount double precision, payment_type integer,
                    source_kind text NOT NULL,
                    loaded_at timestamptz NOT NULL DEFAULT now(),
                    PRIMARY KEY (source_month, source_row_number)
                )
            """).format(sql.Identifier(schema))
            )
            zone_insert = (
                sql.SQL("""
                INSERT INTO {}.raw_zones VALUES %s
                ON CONFLICT (location_id) DO UPDATE SET
                    borough=excluded.borough, zone=excluded.zone, service_zone=excluded.service_zone
            """)
                .format(sql.Identifier(schema))
                .as_string(connection)
            )
            execute_values(cursor, zone_insert, rows(zones))
            cursor.execute(
                sql.SQL(
                    "DELETE FROM {}.raw_trips WHERE pickup_datetime >= %s AND pickup_datetime < %s"
                ).format(sql.Identifier(schema)),
                (start.to_pydatetime(), end.to_pydatetime()),
            )
            columns = sql.SQL(", ").join(sql.Identifier(name) for name in prepared.columns)
            insert = (
                sql.SQL("INSERT INTO {}.raw_trips ({}) VALUES %s")
                .format(sql.Identifier(schema), columns)
                .as_string(connection)
            )
            execute_values(cursor, insert, rows(prepared), page_size=1000)
    return len(prepared)


def load_month(month: str, source: str) -> int:
    """Resolve fixtures or public files, then use the same transactional loader."""
    month_bounds(month)
    if source == "sample":
        trips = pd.read_csv(ROOT / "data/sample/trips.csv")
        zones = pd.read_csv(ROOT / "data/sample/zones.csv")
    elif source == "tlc":
        response = requests.get(f"{TLC_BASE}/trip-data/green_tripdata_{month}.parquet", timeout=120)
        response.raise_for_status()
        trips = pd.read_parquet(io.BytesIO(response.content)).rename(
            columns={
                "VendorID": "vendor_id",
                "lpep_pickup_datetime": "pickup_datetime",
                "lpep_dropoff_datetime": "dropoff_datetime",
                "PULocationID": "pickup_location_id",
                "DOLocationID": "dropoff_location_id",
            }
        )
        response = requests.get(f"{TLC_BASE}/misc/taxi_zone_lookup.csv", timeout=60)
        response.raise_for_status()
        zones = pd.read_csv(io.StringIO(response.text))
    else:
        raise ValueError("Source must be sample or tlc")
    return replace_month(trips, zones, month, source_kind=source)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=["sample", "tlc"], default="sample")
    parser.add_argument(
        "--month", help="YYYY-MM; omitted sample mode loads January and February 2024"
    )
    args = parser.parse_args()
    if args.source == "tlc" and not args.month:
        parser.error("--month is required with --source tlc")
    for month in [args.month] if args.month else ["2024-01", "2024-02"]:
        print(f"Loaded {load_month(month, args.source)} raw trips for {month} ({args.source})")


if __name__ == "__main__":
    main()
