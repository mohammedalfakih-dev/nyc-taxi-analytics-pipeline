# Local runbook

Use Docker Desktop with Linux containers. The root README's sample commands initialize PostgreSQL, ingest both fixture months, build/test dbt and export reports. Ports: PostgreSQL `15432`, optional Streamlit `8503`, optional Airflow `8083`. If a port is already occupied, stop the conflicting local service or update the published port and corresponding host settings.

## Separate public dataset

To keep the synthetic schema available while inspecting a public month:

```sh
docker compose run --rm -e RAW_SCHEMA=taxi_public_raw -e DBT_SCHEMA=taxi_public_analytics pipeline python -m taxi_pipeline.ingest --source tlc --month 2024-01
docker compose run --rm -e RAW_SCHEMA=taxi_public_raw -e DBT_SCHEMA=taxi_public_analytics pipeline dbt build --project-dir dbt --profiles-dir dbt
docker compose run --rm -e RAW_SCHEMA=taxi_public_raw -e DBT_SCHEMA=taxi_public_analytics -e OUTPUT_DIR=reports/generated/public-validation pipeline python -m taxi_pipeline.report
```

Use the same schema pair throughout ingestion, dbt and reporting. TLC network failures or unavailable monthly files fail before raw replacement. Downloaded files are processed in memory rather than committed. Repeated downloads can reflect revised source files; file checksums/version manifests are not recorded.

## Python checks

Requires Python 3.12 and [uv](https://docs.astral.sh/uv/). Build the sample database/marts first. Install the locked environment:

```sh
uv sync --frozen --python 3.12
```

PowerShell:

```powershell
$env:POSTGRES_TEST_URL = 'postgresql://taxi:taxi@127.0.0.1:15432/taxi'
uv run pytest -q
```

POSIX shell:

```sh
POSTGRES_TEST_URL=postgresql://taxi:taxi@127.0.0.1:15432/taxi uv run pytest -q
```

Tests use an isolated temporary schema for rollback checks, and the default sample mart for Streamlit checks. If you override `POSTGRES_URL` or schemas, keep the sample app's database aligned. Never point the fixture-based dashboard checks at your public-data mart. Unit-only runs without `POSTGRES_TEST_URL` explicitly skip the database and dashboard checks.

```sh
uv run ruff check taxi_pipeline dashboards tests orchestration
uv run ruff format --check taxi_pipeline dashboards tests orchestration
docker compose run --rm pipeline dbt build --project-dir dbt --profiles-dir dbt
```

## Airflow

The isolated image pins Airflow 3.0.6 with Python 3.12; dbt dependencies live in a separate `/opt/taxi/.venv` so they do not replace Airflow's own packages. PostgreSQL's initial setup creates the metadata database. An existing volume created before this setup may need that database created manually; do not delete a volume to fix it.

Build, check imports and initialize metadata:

```sh
docker compose build airflow
docker compose run --rm airflow python /opt/taxi/test_dag.py
docker compose run --rm airflow airflow db migrate
```

Run a local fixture month through all three tasks:

```sh
docker compose run --rm airflow python /opt/taxi/run_sample_dag.py
```

Optional local UI:

```sh
docker compose --profile airflow up -d airflow
docker compose logs airflow
```

Open [localhost:8083](http://localhost:8083); the standalone logs provide its generated local credentials. Keep the DAG paused while reviewing. A manual trigger can pass `{"month":"2024-01","source":"sample"}` or `{"month":"2024-01","source":"tlc"}`. Without an override, ingestion uses the run's monthly data interval and the public TLC source. `catchup=False` avoids an automatic historical backfill; it does not wait for TLC publication. Only trigger months known to be published.

Retries are two per task, five minutes apart; a failed run may wait for those retries. Avoid overlapping manual dbt commands with DAG runs.

## Exports, refresh and shutdown

Generated reports live in `reports/generated/` and are ignored by Git. `reports/sample/` holds a saved synthetic example. Re-export after a dbt build; exports are not automatically refreshed by the DAG. Dashboard queries cache for five minutes; use **Refresh data** after a rebuild.

Stop this project's services while preserving data:

```sh
docker compose --profile dashboard --profile airflow stop
```

`docker compose down` removes this project's containers/network while preserving named volumes by default. Do not add `-v` unless you intend to erase the project's stored data.
