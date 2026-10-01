"""Monthly ingestion → dbt run → dbt test; adapted from the Week 12 DAG."""

from datetime import timedelta

import pendulum
from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG

with DAG(
    dag_id="taxi_pipeline",
    schedule="@monthly",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=5)},
    tags=["taxi", "portfolio"],
    is_paused_upon_creation=True,
) as dag:
    ingest = BashOperator(
        task_id="ingest_taxi_month",
        bash_command='/opt/taxi/.venv/bin/python -m taxi_pipeline.ingest --month "$TAXI_MONTH" --source "$TAXI_SOURCE"',
        cwd="/opt/taxi",
        env={
            "TAXI_MONTH": "{{ dag_run.conf.get('month', data_interval_start.strftime('%Y-%m')) }}",
            "TAXI_SOURCE": "{{ dag_run.conf.get('source', 'tlc') }}",
        },
        append_env=True,
    )
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="/opt/taxi/.venv/bin/dbt run --project-dir dbt --profiles-dir dbt",
        cwd="/opt/taxi",
    )
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="/opt/taxi/.venv/bin/dbt test --project-dir dbt --profiles-dir dbt",
        cwd="/opt/taxi",
    )
    ingest >> dbt_run >> dbt_test
