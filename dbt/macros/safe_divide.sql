-- safe_divide(numerator, denominator)
-- Returns numerator / denominator, or NULL when denominator is 0 or NULL.


{% macro safe_divide(numerator, denominator) %}
    ({{ numerator }}::numeric / NULLIF({{ denominator }}::numeric, 0))
{% endmacro %}
