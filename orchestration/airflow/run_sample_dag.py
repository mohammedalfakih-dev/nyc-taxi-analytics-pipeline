"""Execute one sample month through Airflow's local DAG test command."""

import json
import subprocess

subprocess.run(["airflow", "db", "migrate"], check=True)
subprocess.run(
    [
        "airflow",
        "dags",
        "test",
        "taxi_pipeline",
        "2024-01-01",
        "--conf",
        json.dumps({"month": "2024-01", "source": "sample"}),
    ],
    check=True,
)
