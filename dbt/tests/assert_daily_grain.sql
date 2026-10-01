select pickup_borough, pickup_date from {{ ref('fct_daily_borough_stats') }}
group by pickup_borough, pickup_date having count(*) > 1
