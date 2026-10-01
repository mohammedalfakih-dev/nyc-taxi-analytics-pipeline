-- Recreate the Week 11 panels against the consolidated trip mart.
SELECT payment_type_label, count(*) AS trip_count
FROM taxi_analytics.fct_trips GROUP BY 1 ORDER BY 2 DESC;

SELECT dropoff_borough, avg(fare_per_mile) AS avg_fare_per_mile
FROM taxi_analytics.fct_trips GROUP BY 1 ORDER BY 2 DESC;

SELECT extract(hour FROM pickup_datetime) AS pickup_hour,
    avg(trip_duration_minutes) AS avg_trip_duration_minutes
FROM taxi_analytics.fct_trips GROUP BY 1 ORDER BY 1;
