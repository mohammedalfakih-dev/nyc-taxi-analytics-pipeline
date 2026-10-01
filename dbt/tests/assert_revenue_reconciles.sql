select 1 where abs(
    coalesce((select sum(fare_amount) from {{ ref('fct_trips') }}), 0)
    - coalesce((select sum(total_fare) from {{ ref('fct_daily_borough_stats') }}), 0)
) > 0.000001
