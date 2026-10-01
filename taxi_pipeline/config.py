"""One configuration contract for ingestion, reports, and the dashboard."""

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def schema_name(value: str) -> str:
    if not re.fullmatch(r"[a-z][a-z0-9_]{0,62}", value):
        raise ValueError("Schema names must use lowercase letters, digits, and underscores")
    return value


def database_url() -> str:
    return os.getenv("POSTGRES_URL", "postgresql://taxi:taxi@127.0.0.1:15432/taxi")


def raw_schema() -> str:
    return schema_name(os.getenv("RAW_SCHEMA", "taxi_raw"))


def mart_schema() -> str:
    return schema_name(os.getenv("DBT_SCHEMA", "taxi_analytics"))
