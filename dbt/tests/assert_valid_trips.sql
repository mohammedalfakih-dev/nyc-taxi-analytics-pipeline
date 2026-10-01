select * from {{ ref('fct_trips') }}
where fare_amount < 0 or trip_distance < 0
    or (trip_distance = 0 and fare_per_mile is not null)
    or (fare_amount = 0 and tip_pct is not null)
    or trip_duration_minutes < 0
