import streamlit as st
import plotly.express as px
import pandas as pd

def render_rq5(data):
    st.title("🔗 RQ5 — Cross‑Dataset Insights")

    # GOLD tables
    results = data["results"].copy()      # fact_session_results
    races = data["races"].copy()          # dim_races
    circuits = data["circuits"].copy()    # dim_circuits

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------
    if results.empty:
        st.error("❌ Missing fact_session_results table. Run Gold pipeline first.")
        return

    # ---------------------------------------------------------
    # MERGE EVERYTHING INTO ONE MASTER DATAFRAME
    # ---------------------------------------------------------
    df = (
        results
        .merge(races[["season", "round", "race_name", "race_date", "circuit_id"]], 
               on=["season", "round"], how="left")
        .merge(circuits[["circuit_id", "circuit_name", "country_name"]], 
               on="circuit_id", how="left")
    )

    # ---------------------------------------------------------
    # PERFORMANCE INDEX (Weighted)
    # ---------------------------------------------------------
    st.subheader("🔥 Weighted Performance Index (Race + Sprint)")

    df["is_win"] = (df["final_position"] == 1).astype(int)
    df["is_podium"] = (df["final_position"] <= 3).astype(int)

    df["performance_index"] = (
        df["points"]
        + df["is_win"] * 10
        + df["is_podium"] * 5
    )

    perf = (
        df.groupby("driver_name", dropna=False)["performance_index"]
        .sum()
        .reset_index()
        .sort_values("performance_index", ascending=False)
    )

    fig = px.bar(
        perf.head(15),
        x="driver_name",
        y="performance_index",
        title="Top Drivers by Weighted Performance Index",
        color="performance_index",
        color_continuous_scale="Teal",
    )
    st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------------
    # DRIVER–CIRCUIT PERFORMANCE MATRIX
    # ---------------------------------------------------------
    st.subheader("🌍 Driver–Circuit Performance Matrix")

    circuit_matrix = (
        df.groupby(["driver_name", "circuit_name"], dropna=False)["points"]
        .sum()
        .reset_index()
    )

    fig2 = px.density_heatmap(
        circuit_matrix,
        x="circuit_name",
        y="driver_name",
        z="points",
        title="Driver–Circuit Points Heatmap",
        color_continuous_scale="Magma",
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ---------------------------------------------------------
    # CONSTRUCTOR–CIRCUIT SYNERGY
    # ---------------------------------------------------------
    st.subheader("🏗️ Constructor–Circuit Synergy")

    constructor_circuit = (
        df.groupby(["constructor_name", "circuit_name"], dropna=False)["points"]
        .sum()
        .reset_index()
    )

    fig3 = px.scatter(
        constructor_circuit,
        x="circuit_name",
        y="constructor_name",
        size="points",
        color="points",
        title="Constructor–Circuit Synergy (Points)",
        color_continuous_scale="Viridis",
    )
    st.plotly_chart(fig3, use_container_width=True)

    # ---------------------------------------------------------
    # NATIONALITY‑BASED PERFORMANCE
    # ---------------------------------------------------------
    st.subheader("🌎 Nationality‑Based Performance")

    nationality_perf = (
        df.groupby("driver_nationality", dropna=False)["points"]
        .sum()
        .reset_index()
        .sort_values("points", ascending=False)
    )

    fig4 = px.bar(
        nationality_perf,
        x="driver_nationality",
        y="points",
        title="Driver Nationality — Total Points",
        color="points",
        color_continuous_scale="Inferno",
    )
    st.plotly_chart(fig4, use_container_width=True)

    # ---------------------------------------------------------
    # SEASON‑WISE PERFORMANCE TREND
    # ---------------------------------------------------------
    st.subheader("📈 Season‑Wise Performance Trend")

    season_trend = (
        df.groupby("season", dropna=False)["points"]
        .sum()
        .reset_index()
        .sort_values("season")
    )

    fig5 = px.line(
        season_trend,
        x="season",
        y="points",
        title="Total Points Awarded per Season",
        markers=True,
        color_discrete_sequence=["#ff1e00"],
    )
    st.plotly_chart(fig5, use_container_width=True)

    st.success("RQ5 analysis loaded successfully.")
