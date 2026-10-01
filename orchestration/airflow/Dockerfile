FROM apache/airflow:3.0.6-python3.12
COPY --from=ghcr.io/astral-sh/uv:0.8.22 /uv /usr/local/bin/uv
WORKDIR /opt/taxi
COPY --chown=airflow:root pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY --chown=airflow:root taxi_pipeline/ taxi_pipeline/
COPY --chown=airflow:root dbt/ dbt/
COPY --chown=airflow:root data/sample/ data/sample/
COPY --chown=airflow:root orchestration/airflow/dags/ /opt/taxi/dags/
COPY --chown=airflow:root orchestration/airflow/test_dag.py /opt/taxi/test_dag.py
COPY --chown=airflow:root orchestration/airflow/run_sample_dag.py /opt/taxi/run_sample_dag.py
ENV AIRFLOW__CORE__DAGS_FOLDER=/opt/taxi/dags PYTHONPATH=/opt/taxi
