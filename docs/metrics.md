# Metric definitions

All report metrics use the accepted `fct_trips` population. The daily mart groups by pickup borough and source-local pickup date; dashboard payment filters operate on individual records.

| Metric | Calculation | Interpretation |
|---|---|---|
| Total trips | `count(*)` | Accepted source records; not deduplicated physical journeys |
| Total fare | `sum(fare_amount)` | Meter fares in USD, not total payments or profit |
| Average trip distance | `avg(trip_distance)` | Miles; includes zero-distance records |
| Average fare per mile | `avg(fare_amount / trip_distance)` | Mean of defined per-record ratios; zero distances excluded through NULL |
| Average tip percentage | `avg(tip_amount / fare_amount)` | Ratio, multiply by 100 to display percent; zero fares/missing tips excluded |
| Average trip duration | `avg(duration_minutes)` | Nonnegative defined source wall-clock durations |
| Hourly demand | Records per pickup hour | Local hours, missing hours displayed as zero |
| Latest pickup | `max(pickup_datetime)` | Historical coverage, not pipeline freshness |
| Latest ingestion | `max(loaded_at)` | Latest contributing raw load, not latest dbt rebuild |

Mean fare per mile is not `sum(fare_amount) / sum(trip_distance)`. A borough/day average must not be averaged again to obtain the overall trip-level average without weighting by its contributing population. The dashboard reads the trip mart directly to avoid this error.

Cash tips are absent from TLC's recorded tip amounts. A comparison across payment methods cannot measure all real tipping behavior. Unknown payment codes map to `Unknown`; records remain available for auditing.

## Fixture calculation

Eight accepted rows produce $87 in fare and 17 miles: mean distance `17 / 8 = 2.125`. Seven rows have positive distance; their fare/mile ratios sum to 37, so the mean is `37 / 7 = 5.285714…`. Cash yields 3 rows and Credit card 5. These fixture totals verify the calculations, not a claim about NYC travel patterns.
