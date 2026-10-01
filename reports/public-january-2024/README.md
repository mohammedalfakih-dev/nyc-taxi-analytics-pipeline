# Public January 2024 validation snapshot

On 2 October 2026 (Europe/Amsterdam), the Docker pipeline downloaded official TLC `green_tripdata_2024-01.parquet` and the zone lookup, loaded them into separate validation schemas and passed all 14 dbt checks. These aggregate exports are a saved run, not a live dataset.

| Result | Value |
|---|---:|
| Raw records within January pickup bounds | 56,549 |
| Zone references | 265 |
| Negative-fare raw records | 182 |
| Accepted trip records | 56,367 |
| Daily borough/date rows | 163 |
| Total meter fare | $958,855.15 |

The filtering policy excludes negative fares and invalid/missing distances or pickup IDs; it does not trim large positive outliers. The saved mean distance of about 31.59 miles should therefore not be treated as a robust description of a typical taxi ride. Investigating outliers and adding median/percentile metrics is a future analysis step.

Only aggregate exports are committed. The public monthly source is not vendored, and a later source revision could change these results. The original file's full row count may differ from the retained raw count because the loader restricts pickup timestamps to the requested month.
