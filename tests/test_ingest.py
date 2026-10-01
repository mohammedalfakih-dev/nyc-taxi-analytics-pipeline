"""Unit checks and optional PostgreSQL transaction regression checks."""

import os
from contextlib import closing
from uuid import uuid4

import pandas as pd
import psycopg2
import pytest
from psycopg2 import sql

from taxi_pipeline.config import ROOT, schema_name
from taxi_pipeline.ingest import month_bounds, normalize_zones, prepare_month, replace_month


@pytest.mark.parametrize("value", ["2024-00", "2024-13", "24-01", "2024-1", "bad;drop table"])
def test_invalid_months_fail(value):
    with pytest.raises(ValueError):
        month_bounds(value)


def test_month_boundaries_include_first_day_and_exclude_next_month():
    trips = pd.read_csv(ROOT / "data/sample/trips.csv")
    january = prepare_month(trips, "2024-01")
    february = prepare_month(trips, "2024-02")
    assert len(january) == 11
    assert len(february) == 1
    assert january.source_row_number.tolist() == list(range(1, 12))
    assert february.iloc[0].source_row_number == 12


def test_empty_month_cannot_erase_a_previous_partition():
    with pytest.raises(ValueError, match="refusing replacement"):
        prepare_month(pd.read_csv(ROOT / "data/sample/trips.csv"), "2023-01")


def test_zone_duplicates_fail():
    zones = pd.read_csv(ROOT / "data/sample/zones.csv")
    with pytest.raises(ValueError, match="unique"):
        normalize_zones(pd.concat([zones, zones.iloc[:1]]))


@pytest.mark.parametrize("value", ["public; drop table", "Uppercase", "", "a.b"])
def test_invalid_schema_identifiers_fail(value):
    with pytest.raises(ValueError):
        schema_name(value)


def test_monthly_rerun_and_failed_insert_preserve_existing_rows():
    url = os.getenv("POSTGRES_TEST_URL")
    if not url:
        pytest.skip("Set POSTGRES_TEST_URL for PostgreSQL integration verification")
    schema = "taxi_test_" + uuid4().hex[:12]
    trips = pd.read_csv(ROOT / "data/sample/trips.csv")
    zones = pd.read_csv(ROOT / "data/sample/zones.csv")
    try:
        assert replace_month(trips, zones, "2024-01", url, schema) == 11
        assert replace_month(trips, zones, "2024-02", url, schema) == 1
        assert replace_month(trips, zones, "2024-01", url, schema) == 11
        bad = pd.concat([trips, trips.iloc[:1]], ignore_index=True)
        with pytest.raises(psycopg2.errors.UniqueViolation):
            replace_month(bad, zones, "2024-01", url, schema)
        with closing(psycopg2.connect(url)) as connection, connection.cursor() as cursor:
            cursor.execute(
                sql.SQL(
                    "SELECT source_month, count(*) FROM {}.raw_trips GROUP BY 1 ORDER BY 1"
                ).format(sql.Identifier(schema))
            )
            results = cursor.fetchall()
            assert [count for _, count in results] == [11, 1]
    finally:
        with closing(psycopg2.connect(url)) as connection, connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(schema))
                )
