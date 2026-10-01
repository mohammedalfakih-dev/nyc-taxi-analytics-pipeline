"""Export model outputs and data-quality findings for a reviewable run."""

import json
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

from taxi_pipeline.config import database_url, mart_schema, raw_schema


def export_reports(output_dir=None):
    output_dir = Path(output_dir or os.getenv("OUTPUT_DIR", "reports/generated"))
    output_dir.mkdir(parents=True, exist_ok=True)
    engine = create_engine(database_url())
    raw, mart = raw_schema(), mart_schema()
    with engine.connect() as connection:
        daily = pd.read_sql(
            text(
                f'SELECT * FROM "{mart}".fct_daily_borough_stats ORDER BY pickup_date, pickup_borough'
            ),
            connection,
        )
        daily.to_csv(output_dir / "daily_borough_stats.csv", index=False)
        headline = pd.read_sql(
            text(f"""
            SELECT count(*) AS total_trips, sum(fare_amount) AS total_fare,
                avg(trip_distance) AS avg_trip_distance, avg(fare_per_mile) AS avg_fare_per_mile,
                max(pickup_datetime) AS latest_pickup, max(loaded_at) AS latest_ingestion
            FROM "{mart}".fct_trips
        """),
            connection,
        )
        headline.to_csv(output_dir / "headline_metrics.csv", index=False)
        quality = pd.read_sql(
            text(f"""
            SELECT count(*) AS raw_rows,
                count(*) FILTER (WHERE fare_amount < 0) AS negative_fares,
                count(*) FILTER (WHERE pickup_location_id IS NULL) AS missing_pickup_ids,
                count(*) FILTER (WHERE trip_distance < 0) AS negative_distances,
                count(*) FILTER (WHERE pickup_location_id IS NOT NULL AND z.location_id IS NULL) AS unknown_pickup_ids
            FROM "{raw}".raw_trips t LEFT JOIN "{raw}".raw_zones z ON t.pickup_location_id=z.location_id
        """),
            connection,
        )
        quality.to_csv(output_dir / "data_quality.csv", index=False)
        sources = pd.read_sql(
            text(
                f'SELECT source_kind, source_month, count(*) AS raw_rows FROM "{raw}".raw_trips GROUP BY 1,2 ORDER BY 1,2'
            ),
            connection,
        )
        sources.to_csv(output_dir / "source_scope.csv", index=False)
    engine.dispose()
    result = {
        "total_trips": int(headline.iloc[0].total_trips),
        "total_fare": float(headline.iloc[0].total_fare or 0),
    }
    (output_dir / "summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))
    return result


if __name__ == "__main__":
    export_reports()
