# Synthetic sample outputs

Saved after a successful local Docker ingestion, dbt build and report export on 2 October 2026 (Europe/Amsterdam). These files describe the deliberately small synthetic fixture in `data/sample/`, not measured NYC demand.

- `summary.json`: 8 accepted records and $87.00 total fare.
- `daily_borough_stats.csv`: five borough/date aggregates from those same records.
- `headline_metrics.csv`: trip-level averages and coverage/ingestion timestamps.
- `data_quality.csv`: raw input quality findings.
- `source_scope.csv`: the two synthetic source months.

Timestamps reflect that saved run. A fresh run has a different ingestion timestamp but the same fixture metrics. Follow the root README to rebuild outputs into `reports/generated/`.
