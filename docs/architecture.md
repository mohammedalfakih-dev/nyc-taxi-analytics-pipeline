# Architecture and contracts

The Python loader reads either local CSV fixtures or one green-taxi Parquet file plus the TLC zone CSV. It normalizes names, selects the requested pickup month and writes PostgreSQL tables. Network requests and preparation happen before the replacement transaction.

Within the transaction, a schema-level advisory lock serializes loaders, zone rows are upserted, the requested pickup month is deleted and prepared records are inserted. An insert failure rolls back the deletion and zone changes. An empty month is rejected before touching the database. Repeating a month replaces its source rows; it does not append them. This is not business-key deduplication.

`raw_trips → stg_trips → fct_trips → fct_daily_borough_stats`

`raw_zones → stg_zones → dim_zones → fct_trips`

Staging models are views. Dimension and fact models are rebuilt tables. `fct_trips` performs the pickup-zone inner join and dropoff-zone left join; the daily mart reads those accepted trip records. The dashboard queries only the trip mart with bound payment-filter parameters. Report exports include both daily metrics and raw quality counts.

Airflow runs ingestion, then `dbt run`, then `dbt test`. A failed test marks that DAG run as failed but does not roll back an already committed raw month or all rebuilt marts. A full atomic publish across every model is outside this project's scope. Dashboard queries can briefly fail while tables are rebuilt; caching reduces repeated reads, not this publishing gap.

The loader is protected against two simultaneous writers. Manual dbt runs are not locked against an Airflow dbt run, so avoid concurrent rebuilds. Airflow's one-active-run setting limits its own runs only.

## Local settings

Default schemas are `taxi_raw` and `taxi_analytics`; names accept lowercase letters, digits and underscores, starting with a letter. Python uses `POSTGRES_URL`; dbt uses `PG_HOST`, `PG_PORT`, `PG_USER`, `PG_PASSWORD`, `PG_DATABASE`. Keep those settings pointed at the same database. `.env.example` documents development values; Compose declares its own local environment. It does not automatically inject arbitrary `.env` settings into these services.

PostgreSQL, dashboard and Airflow ports bind to localhost. The bundled database password is a local demo value. Airflow metadata lives in a separate `airflow` database; both database and Airflow runtime volumes are preserved on stop.

## Scaling considerations

The loader materializes one monthly Parquet file in memory and uses batched inserts. dbt fully rebuilds tables. Larger deployments would benefit from object-storage manifests/checksums, partitioned loads, late-data reprocessing, incremental marts, reader-safe publishing, monitoring and managed credentials. These are future improvements, not features claimed by this demo.
