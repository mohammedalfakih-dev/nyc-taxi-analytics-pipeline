-- Trip-level contract required by the Week 11 dashboard.
select t.*,
    pickup.borough as pickup_borough,
    coalesce(dropoff.borough, 'Unknown') as dropoff_borough,
    case t.payment_type
        when 0 then 'Flex fare' when 1 then 'Credit card' when 2 then 'Cash'
        when 3 then 'No charge' when 4 then 'Dispute' when 6 then 'Voided trip'
        else 'Unknown'
    end as payment_type_label,
    {{ safe_divide('t.fare_amount', 't.trip_distance') }} as fare_per_mile,
    case when t.dropoff_datetime >= t.pickup_datetime
        then extract(epoch from (t.dropoff_datetime - t.pickup_datetime)) / 60.0
        else null
    end as trip_duration_minutes
from {{ ref('stg_trips') }} as t
inner join {{ ref('dim_zones') }} as pickup on t.pickup_location_id = pickup.location_id
left join {{ ref('dim_zones') }} as dropoff on t.dropoff_location_id = dropoff.location_id
