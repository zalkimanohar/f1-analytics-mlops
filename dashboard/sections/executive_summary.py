import streamlit as st
import pandas as pd
from utils import f1_fig

# ---------------------------------------------------------
# EXECUTIVE SUMMARY (FINAL, FIXED)
# ---------------------------------------------------------
def render_executive_summary(data):
    st.title("📘 Executive Summary")

    drivers = data["drivers"]
    constructors = data["constructors"]
    races = data["races"]
    results = data["results"]

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------
    if results.empty or races.empty or drivers.empty or constructors.empty:
        st.error("❌ Missing required Gold tables. Please run the full pipeline first.")
        return

    # ---------------------------------------------------------
    # KEY METRICS
    # ---------------------------------------------------------
    st.subheader("🏎️ Key Metrics Overview")

    total_drivers = drivers["driver_id"].nunique()
    total_constructors = constructors["constructor_id"].nunique()
    total_races = races[["season", "round"]].drop_duplicates().shape[0]
    total_points = results["points"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Drivers", total_drivers)
    col2.metric("Constructors", total_constructors)
    col3.metric("Races", total_races)
    col4.metric("Total Points Awarded", int(total_points))

    # ---------------------------------------------------------
    # TOP DRIVER
    # ---------------------------------------------------------
    st.subheader("🏁 Top Driver")

    driver_perf = (
        results.groupby("driver_id")["points"]
        .sum()
        .reset_index()
        .merge(
            drivers[["driver_id", "given_name", "family_name"]],
            on="driver_id",
            how="left"
        )
    )
    driver_perf["driver_name"] = driver_perf["given_name"] + " " + driver_perf["family_name"]
    driver_perf = driver_perf.sort_values("points", ascending=False)

    top_driver = driver_perf.iloc[0]

    st.success(
        f"🏎️ **{top_driver['driver_name']}** leads with **{top_driver['points']} points**."
    )

    # ---------------------------------------------------------
    # TOP CONSTRUCTOR
    # ---------------------------------------------------------
    st.subheader("🏆 Top Constructor")

    constructor_perf = (
        results.groupby("constructor_id")["points"]
        .sum()
        .reset_index()
        .merge(
            constructors[["constructor_id", "constructor_name"]],
            on="constructor_id",
            how="left"
        )
        .sort_values("points", ascending=False)
    )

    top_constructor = constructor_perf.iloc[0]

    st.info(
        f"🏆 **{top_constructor['constructor_name']}** leads constructors with **{top_constructor['points']} points**."
    )

    # ---------------------------------------------------------
    # POINTS DISTRIBUTION ACROSS DRIVERS
    # ---------------------------------------------------------
    st.subheader("📊 Points Distribution Across Drivers")

    fig = f1_fig("Driver Points Distribution")
    fig.add_bar(
        x=driver_perf["driver_name"].head(15),
        y=driver_perf["points"].head(15),
        marker_color="#ff1e00"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "📌 *This chart highlights the most dominant drivers in the dataset.*"
    )

    st.success("Executive Summary loaded successfully.")
