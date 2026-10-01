-- Grain: one pickup borough per calendar date; metrics share the trip mart population.
select pickup_borough, pickup_datetime::date as pickup_date,
    count(*) as trip_count, sum(fare_amount) as total_fare,
    avg(tip_pct) as avg_tip_pct, avg(trip_distance) as avg_trip_distance
from {{ ref('fct_trips') }}
group by pickup_borough, pickup_datetime::date
