import streamlit as st
import plotly.express as px
import pandas as pd

def render_rq3(data):
    st.title("🌍 RQ3 — Circuit Geography & Regional Performance")

    # GOLD tables
    circuits = data["circuits"]          # GOLD dim_circuits
    races = data["races"]                # GOLD dim_races
    results = data["results"]            # GOLD fact_session_results

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------
    if circuits.empty or races.empty or results.empty:
        st.error("❌ Missing required Gold tables. Please run the full pipeline first.")
        return

    # ---------------------------------------------------------
    # PREPARE RACE‑LEVEL POINTS
    # ---------------------------------------------------------
    race_points = (
        results.groupby(["season", "round"], dropna=False)["points"]
        .sum()
        .reset_index()
    )

    # ---------------------------------------------------------
    # MERGE RACES + CIRCUITS + POINTS
    # GOLD dim_races contains: circuit_id, race_name, race_date, country
    # GOLD dim_circuits contains: circuit_id, circuit_name, latitude, longitude, country_name
    # ---------------------------------------------------------
    df = (
        races
        .merge(circuits, on="circuit_id", how="left", suffixes=("_race", "_circuit"))
        .merge(race_points, on=["season", "round"], how="left")
    )

    # ---------------------------------------------------------
    # COUNTRY COLUMN FIX
    # ---------------------------------------------------------
    if "country_name" in df.columns:
        country_col = "country_name"
    elif "country" in df.columns:
        country_col = "country"
    else:
        country_col = None

    # ---------------------------------------------------------
    # 1) COUNTRY‑LEVEL GEO PERFORMANCE MAP
    # ---------------------------------------------------------
    st.subheader("🗺️ Circuit Performance by Country")

    if country_col:
        fig = px.choropleth(
            df,
            locations=country_col,
            locationmode="country names",
            color="points",
            hover_name="race_name",
            title="Circuit Performance — Points by Host Country",
            color_continuous_scale="Viridis",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠ No country column found — cannot render geo map.")

    # ---------------------------------------------------------
    # 2) CIRCUIT COMPETITIVENESS INDEX (CCI)
    # ---------------------------------------------------------
    st.subheader("🔥 Circuit Competitiveness Index (CCI)")

    circuit_comp = (
        results
        .merge(races[["season", "round", "circuit_id"]], on=["season", "round"])
        .groupby("circuit_id")["final_position"]
        .std()
        .reset_index()
        .rename(columns={"final_position": "competitiveness"})
    )

    circuit_comp["competitiveness"] = circuit_comp["competitiveness"].fillna(0)

    circuit_comp = circuit_comp.merge(
        circuits[["circuit_id", "circuit_name"]],
        on="circuit_id",
        how="left"
    )

    fig2 = px.bar(
        circuit_comp.sort_values("competitiveness"),
        x="circuit_name",
        y="competitiveness",
        title="Circuit Competitiveness Index (Lower = Tighter Racing)",
        color="competitiveness",
        color_continuous_scale="Plasma",
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ---------------------------------------------------------
    # 3) COUNTRY‑WISE PERFORMANCE
    # ---------------------------------------------------------
    st.subheader("🌎 Country‑Wise Performance")

    if country_col:
        region_perf = (
            df.groupby(country_col)["points"]
            .sum()
            .reset_index()
            .sort_values("points", ascending=False)
        )

        fig3 = px.bar(
            region_perf,
            x=country_col,
            y="points",
            title="Total Points Awarded by Country",
            color="points",
            color_continuous_scale="Inferno",
        )
        st.plotly_chart(fig3, use_container_width=True)

    # ---------------------------------------------------------
    # 4) DRIVER–CIRCUIT AFFINITY MAP
    # ---------------------------------------------------------
    st.subheader("🔗 Driver–Circuit Affinity")

    driver_affinity = (
        results
        .merge(races[["season", "round", "circuit_id"]], on=["season", "round"])
        .merge(circuits[["circuit_id", "circuit_name"]], on="circuit_id")
        .groupby(["driver_name", "circuit_name"], dropna=False)["points"]
        .sum()
        .reset_index()
    )

    fig4 = px.density_heatmap(
        driver_affinity,
        x="circuit_name",
        y="driver_name",
        z="points",
        title="Driver–Circuit Affinity Heatmap",
        color_continuous_scale="Magma",
    )
    st.plotly_chart(fig4, use_container_width=True)

    st.success("RQ3 analysis loaded successfully.")
