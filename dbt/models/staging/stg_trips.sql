-- One retained source record; duplicate-looking business events are not silently deleted.
select *,
    source_month::text || ':' || source_row_number::text as trip_id,
    {{ safe_divide('tip_amount', 'fare_amount') }} as tip_pct
from {{ source('taxi', 'raw_trips') }}
where pickup_datetime is not null
    and pickup_location_id is not null
    and fare_amount >= 0
    and trip_distance >= 0
