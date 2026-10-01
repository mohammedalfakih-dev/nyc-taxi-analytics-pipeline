# Source work and integration

This portfolio project builds on Mohammed Alfakih's completed HackYourFuture Data Track solutions. The course provided assignment scaffolds and learning tasks. This repository adapts the completed solutions for a shared local runtime; it does not claim that the course scaffolds were authored from scratch.

| Week | Original solution branch | Snapshot commit | Contribution carried forward |
|---|---|---|---|
| 9 | [SQL solution](https://github.com/mohammedalfakih-dev/c55-data-week-9/tree/week9/mohammed-alfakih) | `2e4e2add205a42ee6ef89f3816b137aefda21689` | Data-quality audits, fact/dimension design and dictionary concepts |
| 10 | [dbt solution](https://github.com/mohammedalfakih-dev/c55-data-week-10/tree/week10/mohammed-alfakih) | `27113a7f0805cc04074d6bf78631bdd4948846c0` | Staging, borough/day aggregation, safe division and model tests |
| 11 | [Dashboard solution](https://github.com/mohammedalfakih-dev/c55-data-week-11/tree/week11/mohammed-alfakih) | `deb6ffef18d6d37cd98c28256a4a3a4202a063dd` | SQL KPIs, payment filter, hourly chart and Metabase question designs |
| 12 | [Airflow solution](https://github.com/mohammedalfakih-dev/c55-data-week-12/tree/week12/mohammedalfakih) | `d5ff5c36db9963f9d2ad1e5f96ebba4d63141bdf` | Monthly delete/insert ingestion, sequential dbt tasks, retries and run limits |

Original repositories and their Git histories are preserved. The links point to solution branches rather than unfinished default-branch assignment templates. This is a consolidated project, not a byte-for-byte archive of every assignment file.

## Changes made for integration

- Replaced dependencies on class-hosted databases, shared schemas and Astro deployment with a local PostgreSQL service and public TLC sources.
- Consolidated overlapping Week 10/12 dbt projects into one model graph.
- Added the trip-level `fct_trips` contract required by the Week 11 app. The original daily aggregation alone could not supply the app's trip-level payment and hour filters.
- Made daily aggregates derive from that same trip population, with a reconciliation test.
- Expanded the loader's fields to support distance, payment, tips, dropoff and duration metrics. Loaded zone references in the same transaction.
- Added source-row keys, source labels, ingestion timestamps, schema validation and transaction locking.
- Added an explicit synthetic fixture with quality edge cases, local reports and Python regression checks.
- Adapted the Streamlit app to the shared model, current supported layout APIs and explicit data-source labels.
- Adapted the Airflow DAG to its pinned Airflow 3 Docker runtime and added import/execution checks.
- Replaced assignment instructions as the root README with project purpose, setup, contracts and limitations. Instructor autograders and private class links are not needed by the runnable project.

## Historical evidence

[Metabase coursework screenshot](../assets/metabase-coursework.png) is retained from the Week 11 solution. It shows the earlier class dataset and dashboard, not the new synthetic run. Private class dashboards/recordings are not public demos for this repository.

The original Week 12 backfill counts and Week 9 audit counts remain in the source repositories. They are historical coursework evidence and must not be mixed with this repository's fixture counts or new public-data checks.

NYC TLC publishes the public data. The six fixture zone labels follow that reference lookup; fixture trip rows are synthetic. No raw public trip dataset or personal database credentials are committed here.
