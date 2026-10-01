# Data dictionary

Source: [NYC TLC green-taxi trip records](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) and [official green-taxi dictionary](https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_green.pdf). The pipeline selects fields needed by its models; it does not retain every published column.

| Canonical field | TLC field | Meaning |
|---|---|---|
| `vendor_id` | `VendorID` | Provider code, not a vehicle or driver identifier |
| `pickup_datetime` | `lpep_pickup_datetime` | Meter pickup time; stored as timezone-naive local timestamp |
| `dropoff_datetime` | `lpep_dropoff_datetime` | Meter dropoff time |
| `pickup_location_id` | `PULocationID` | TLC pickup zone code |
| `dropoff_location_id` | `DOLocationID` | TLC dropoff zone code |
| `passenger_count` | `passenger_count` | Reported passenger count |
| `trip_distance` | `trip_distance` | Reported trip distance in miles |
| `fare_amount` | `fare_amount` | Meter fare in USD; not total customer payment |
| `tip_amount` | `tip_amount` | Recorded tips; cash tips are not included |
| `total_amount` | `total_amount` | Reported total charge; cash tips are not included |
| `payment_type` | `payment_type` | Payment code mapped to labels in the trip mart |
| `source_month` | Added | Requested file/month partition date |
| `source_row_number` | Added | One-based source row position, assigned before month filtering |
| `source_kind` | Added | `sample` or `tlc` |
| `loaded_at` | Added | Database transaction ingestion timestamp, with timezone |

`raw_zones` stores `location_id`, `borough`, `zone` and `service_zone` from the zone lookup. Its primary key is `location_id`.

## Model grains and keys

| Model | Grain / key |
|---|---|
| `raw_trips` | One retained source record; key `(source_month, source_row_number)` |
| `stg_trips` | One source record passing basic fare, distance and pickup checks |
| `dim_zones` | One lookup location; key `location_id` |
| `fct_trips` | One cleaned source record with a matching pickup lookup; key `trip_id` |
| `fct_daily_borough_stats` | One pickup borough per pickup date; key `(pickup_borough, pickup_date)` |

`trip_id` joins the source month and row number. It locates a record in a file, not a guaranteed physical trip. A revised file can move source rows. Two records with identical vendor and pickup/dropoff times remain separate and can be inspected with the duplicate-candidate SQL audit.

Trip-derived fields: pickup/dropoff boroughs, payment label, `tip_pct` (tip/fare ratio), `fare_per_mile`, and nonnegative `trip_duration_minutes`. Unknown dropoff zones receive `Unknown`. Invalid durations receive NULL rather than dropping the record. Zero fare or distance gives NULL for the corresponding ratio.

Timezone-naive timestamps preserve source wall-clock values; DST-ambiguous times are not resolved into UTC instants. Duration metrics therefore share that limitation.
