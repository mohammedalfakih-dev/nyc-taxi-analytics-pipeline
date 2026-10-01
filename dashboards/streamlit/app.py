"""Taxi metrics dashboard adapted from the completed Week 11 app."""

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

from taxi_pipeline.config import database_url, mart_schema

st.set_page_config(page_title="NYC taxi analytics", layout="wide")
st.title("NYC taxi analytics")
st.caption("Explore trip volume, fare patterns, and hourly demand for green-taxi records.")


@st.cache_resource
def get_engine(url):
    return create_engine(url, pool_pre_ping=True)


@st.cache_data(ttl=300, max_entries=64)
def run_query(sql, params, url):
    with get_engine(url).connect() as connection:
        return pd.read_sql(text(sql), connection, params=params)


url = database_url()
schema = mart_schema()
table = f'"{schema}".fct_trips'
try:
    options = run_query(f"SELECT DISTINCT payment_type_label FROM {table} ORDER BY 1", {}, url)
    scope = run_query(f"SELECT DISTINCT source_kind FROM {table} ORDER BY 1", {}, url)
except Exception:
    st.error("The taxi reports are unavailable. Follow the README's setup and dbt build steps.")
    st.stop()

if scope.empty:
    st.info("No trips are available yet. Load a month and build the reports.")
    st.stop()
st.caption(
    "Dataset: "
    + ", ".join(
        scope.source_kind.replace({"sample": "synthetic fixture", "tlc": "public TLC records"})
    )
)

selection = st.sidebar.selectbox("Payment type", ["All", *options.payment_type_label.tolist()])
if st.sidebar.button("Refresh data"):
    run_query.clear()
    st.rerun()
params = {} if selection == "All" else {"payment_type": selection}
where = "" if selection == "All" else "WHERE payment_type_label = :payment_type"

headline = run_query(
    f"""
    SELECT count(*) AS total_trips, avg(trip_distance) AS avg_trip_distance,
        avg(fare_per_mile) AS avg_fare_per_mile,
        max(pickup_datetime) AS latest_pickup, max(loaded_at) AS latest_ingestion
    FROM {table} {where}
""",
    params,
    url,
).iloc[0]

with st.container(horizontal=True):
    st.metric("Total trips", f"{int(headline.total_trips):,}", border=True)
    distance = (
        "—" if pd.isna(headline.avg_trip_distance) else f"{headline.avg_trip_distance:.2f} miles"
    )
    fare = "—" if pd.isna(headline.avg_fare_per_mile) else f"${headline.avg_fare_per_mile:.2f}"
    st.metric("Average trip distance", distance, border=True)
    st.metric("Average fare per mile", fare, border=True)

hourly = (
    run_query(
        f"""
    SELECT extract(hour from pickup_datetime)::integer AS pickup_hour, count(*) AS trip_count
    FROM {table} {where} GROUP BY 1 ORDER BY 1
""",
        params,
        url,
    )
    .set_index("pickup_hour")
    .reindex(range(24), fill_value=0)
    .reset_index()
)
st.subheader("Trips by pickup hour")
st.line_chart(
    hourly, x="pickup_hour", y="trip_count", x_label="Pickup hour (local time)", y_label="Trips"
)

boroughs = run_query(
    f"""
    SELECT pickup_borough, count(*) AS trip_count, sum(fare_amount) AS total_fare
    FROM {table} {where} GROUP BY 1 ORDER BY trip_count DESC
""",
    params,
    url,
)
st.subheader("Pickup boroughs")
st.dataframe(
    boroughs,
    hide_index=True,
    column_config={"total_fare": st.column_config.NumberColumn("Total fare", format="$%.2f")},
)

st.subheader("Data coverage")
if pd.notna(headline.latest_pickup):
    st.write(f"Latest pickup: {headline.latest_pickup:%Y-%m-%d %H:%M}")
    st.write(f"Latest raw-data ingestion: {headline.latest_ingestion:%Y-%m-%d %H:%M %Z}")
else:
    st.info("No trips match the selected payment type.")
st.caption(
    "Pickup timestamps describe historical coverage. Ingestion time records the loader run, not a dbt build. Results cache for up to five minutes."
)
