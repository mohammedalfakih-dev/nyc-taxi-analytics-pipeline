FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.8.22 /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY taxi_pipeline/ taxi_pipeline/
COPY dbt/ dbt/
COPY dashboards/ dashboards/
COPY data/sample/ data/sample/
ENV PATH="/app/.venv/bin:$PATH" PYTHONPATH=/app
CMD ["python", "-m", "taxi_pipeline.ingest", "--source", "sample"]
