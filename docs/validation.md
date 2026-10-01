# Validation scope

Verified locally on 2 October 2026 (Europe/Amsterdam), using the locked Python environment, PostgreSQL 16 and the Docker images in this repository.

| Check | Result |
|---|---|
| Python tests | 14 passed, including PostgreSQL rerun/rollback and the actual Streamlit app via AppTest |
| Ruff lint / formatting | Passed for pipeline, dashboard, tests and orchestration code |
| Sample dbt build | 5 models built; 14 data checks passed |
| Core Docker run | Sample ingestion, dbt build/tests and report export passed |
| Sample outputs | 12 raw records → 8 accepted records; $87.00 fare |
| Public TLC January 2024 | 56,549 raw records → 56,367 accepted records; all 14 dbt checks passed |
| Airflow image | Built with Airflow 3.0.6 / Python 3.12; DAG import and dependency checks passed |
| Airflow local DAG execution | January sample ingestion → dbt run → dbt test all succeeded through `airflow dags test` |

The Windows host's first public-file request encountered a connection reset. The same loader then succeeded inside the Linux Docker container, and the saved public exports come from that successful run.

AppTest verified the real app's three headline metrics and Cash/Credit card filters against the local sample mart without starting a browser server. A visual browser review, hosted dashboard, Metabase deployment, continuous scheduler operation, production credentials and production-scale performance were not verified. The Airflow check ran one local historical sample DAG, not a live monthly production service or a full historical backfill.

CI is configured to repeat fixture, database, dashboard and image/DAG checks on pull requests and pushes to main. A local pass does not establish that a GitHub Actions run has completed; inspect the PR checks separately.

Saved [synthetic exports](../reports/sample/) and [public January aggregate exports](../reports/public-january-2024/) are snapshots. Original classroom screenshots and backfill counts are historical evidence as described in [provenance](provenance.md).
