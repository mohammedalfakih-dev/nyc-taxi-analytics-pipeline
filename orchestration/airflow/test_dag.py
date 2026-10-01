"""Run inside the Airflow image to check imports and task dependencies."""

from airflow.models import DagBag

bag = DagBag(dag_folder="/opt/taxi/dags")
assert not bag.import_errors, bag.import_errors
dag = bag.dags.get("taxi_pipeline")
assert dag is not None
assert dag.max_active_runs == 1
assert set(dag.task_ids) == {"ingest_taxi_month", "dbt_run", "dbt_test"}
assert dag.get_task("ingest_taxi_month").downstream_task_ids == {"dbt_run"}
assert dag.get_task("dbt_run").downstream_task_ids == {"dbt_test"}
print("DAG import and dependencies passed")
