import streamlit as st
import plotly.express as px
import pandas as pd

def render_rq4(df):
    st.title("⚡ RQ4 — Sprint Race Analysis")

    # ---------------------------------------------------------
    # FILTER ONLY SPRINT SESSIONS FROM GOLD
    # ---------------------------------------------------------
    sprint_df = df[df["session_type"] == "SPRINT"].copy()

    if sprint_df.empty:
        st.warning("⚠ No sprint data available in this batch.")
        return

    # ---------------------------------------------------------
    # 1) GRID vs FINAL POSITION — Sprint Edition
    # ---------------------------------------------------------
    st.subheader("📉 Sprint: Grid Position vs Final Position")

    fig = px.scatter(
        sprint_df,
        x="grid_position",
        y="final_position",
        color="points",
        hover_name="driver_name",
        title="Sprint — Grid vs Final Position",
        color_continuous_scale="Turbo",
        trendline="ols",
    )
    fig.update_yaxes(autorange="reversed")  # P1 at top
    st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------------
    # 2) SPRINT POINTS DISTRIBUTION
    # ---------------------------------------------------------
    st.subheader("🔥 Sprint Points Distribution")

    sprint_points = (
        sprint_df.groupby("driver_name", dropna=False)["points"]
        .sum()
        .reset_index()
        .sort_values("points", ascending=False)
    )

    fig2 = px.bar(
        sprint_points.head(15),
        x="driver_name",
        y="points",
        title="Top Drivers — Sprint Points",
        color="points",
        color_continuous_scale="Reds",
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ---------------------------------------------------------
    # 3) SPRINT vs RACE PERFORMANCE COMPARISON
    # ---------------------------------------------------------
    st.subheader("🔗 Sprint vs Race Performance Comparison")

    race_df = (
        df[df["session_type"] == "RACE"]
        .groupby("driver_name", dropna=False)["points"]
        .sum()
        .reset_index()
        .rename(columns={"points": "race_points"})
    )

    sprint_vs_race = (
        sprint_points
        .merge(race_df, on="driver_name", how="left")
        .fillna(0)
    )

    fig3 = px.scatter(
        sprint_vs_race,
        x="points",
        y="race_points",
        hover_name="driver_name",
        title="Sprint Points vs Race Points",
        color="race_points",
        color_continuous_scale="Viridis",
        size="race_points"
    )
    st.plotly_chart(fig3, use_container_width=True)

    # ---------------------------------------------------------
    # 4) CONSTRUCTOR SPRINT PERFORMANCE
    # ---------------------------------------------------------
    st.subheader("🏆 Constructor Sprint Performance")

    constructor_sprint = (
        sprint_df.groupby("constructor_name", dropna=False)["points"]
        .sum()
        .reset_index()
        .sort_values("points", ascending=False)
    )

    fig4 = px.bar(
        constructor_sprint,
        x="constructor_name",
        y="points",
        title="Constructor Sprint Points",
        color="points",
        color_continuous_scale="Blues",
    )
    st.plotly_chart(fig4, use_container_width=True)

    # ---------------------------------------------------------
    # 5) SPRINT DNF ANALYSIS
    # ---------------------------------------------------------
    st.subheader("💥 Sprint DNF Analysis")

    sprint_df["is_dnf"] = sprint_df["status"].str.contains("DNF", case=False, na=False)

    sprint_dnf = (
        sprint_df.groupby("driver_name", dropna=False)["is_dnf"]
        .sum()
        .reset_index()
        .sort_values("is_dnf", ascending=False)
    )

    fig5 = px.bar(
        sprint_dnf,
        x="driver_name",
        y="is_dnf",
        title="Sprint DNFs by Driver",
        color="is_dnf",
        color_continuous_scale="Inferno",
    )
    st.plotly_chart(fig5, use_container_width=True)

    st.success("RQ4 analysis loaded successfully.")
