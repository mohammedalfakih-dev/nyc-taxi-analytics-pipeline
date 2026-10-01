# Data quality

The loader retains pickup timestamps inside `[month start, next month start)`. Invalid/missing or out-of-month pickup timestamps are excluded before raw insertion. Numeric fields are normalized; invalid integer representations can fail preparation rather than silently loading misleading values. Missing required columns, duplicate zone IDs and an empty prepared month fail before replacement.

Staging retains records with a pickup location, nonnegative fare and nonnegative distance. SQL comparisons also exclude NULL fares/distances. The trip mart requires a matching pickup-zone reference. It preserves unknown dropoff zones and duplicate-looking business keys. Negative or missing tips, passenger counts and payment codes are not additional row exclusions; these fields require interpretation rather than a blanket assertion that all retained records are fully valid.

## Synthetic fixture audit

| Check | Raw findings |
|---|---:|
| Loaded records | 12 |
| Negative fare | 1 |
| Missing pickup ID | 1 |
| Negative distance | 1 |
| Non-null pickup ID absent from lookup | 1 |
| Accepted trip records | 8 |

The fixture contains a zero-distance, zero-fare row to test NULL ratios, an unknown dropoff that remains in the mart, and two duplicate-looking records that remain separate. Raw audit counts can overlap in other datasets and must not simply be subtracted from the raw count.

Run [sql/data_quality.sql](../sql/data_quality.sql) for raw checks, candidate duplicates and daily totals. [Saved quality CSV](../reports/sample/data_quality.csv) records the fixture result. These queries default to the sample schema names; adapt them when using separate schemas.

## Automated assertions

The dbt checks validate lookup and trip key uniqueness/non-nullness, essential reporting fields, daily composite grain, nonnegative modeled fare/distance/duration, safe zero denominators, and agreement of total trips/fares between daily and trip marts. They do not verify every source field or establish that two distinct records represent two distinct physical journeys.

The Python PostgreSQL regression loads January and February, repeats January, forces an insert-key error and verifies that both prior partitions survive the rollback. Dashboard checks exercise the real application with the fixture, including Cash and Credit card filters.
