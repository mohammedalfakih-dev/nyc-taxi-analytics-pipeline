-- Adapted Week 9 audits against the consolidated loader's source schema.
SELECT count(*) AS raw_rows,
    count(*) FILTER (WHERE fare_amount < 0) AS negative_fares,
    count(*) FILTER (WHERE pickup_location_id IS NULL) AS missing_pickup_ids,
    count(*) FILTER (WHERE trip_distance < 0) AS negative_distances
FROM taxi_raw.raw_trips;

SELECT t.pickup_location_id, count(*) AS trip_count
FROM taxi_raw.raw_trips t
LEFT JOIN taxi_raw.raw_zones z ON t.pickup_location_id=z.location_id
WHERE t.pickup_location_id IS NOT NULL AND z.location_id IS NULL
GROUP BY 1;

-- Candidate business keys are an audit, not a guaranteed trip identifier.
SELECT vendor_id, pickup_datetime, dropoff_datetime, count(*) AS duplicate_count
FROM taxi_raw.raw_trips
GROUP BY 1,2,3 HAVING count(*) > 1;

SELECT sum(trip_count) AS daily_total, sum(total_fare) AS total_fare
FROM taxi_analytics.fct_daily_borough_stats;
