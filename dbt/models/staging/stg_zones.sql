select location_id, borough, zone, service_zone
from {{ source('taxi', 'raw_zones') }}
