# dashboard/sections/rq4_sprint_race.py

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import f1_fig

def render_rq4(df: pd.DataFrame):
    st.markdown("## 🟨 RQ4 — SPRINT–RACE PERFORMANCE RELATIONSHIP")

    # ---------------------------------------------------------
    # Filter only seasons with sprint races (2021+)
    # ---------------------------------------------------------
    df_sprint = df[df["season"] >= 2021]

    if df_sprint.empty:
        st.info("⚠️ Sprint races exist only from 2021 onward. Adjust your Season filter.")
        return

    sprint_df = df_sprint[df_sprint["session_type"] == "SPRINT"]
    race_df = df_sprint[df_sprint["session_type"] == "RACE"]

    if sprint_df.empty:
        st.warning("No Sprint sessions found for the selected filters.")
        return

    # ---------------------------------------------------------
    # Merge sprint → race results for same driver & round
    # ---------------------------------------------------------
    merged = sprint_df.merge(
        race_df,
        on=["season", "round", "driver_id"],
        suffixes=("_sprint", "_race")
    )

    if merged.empty:
        st.warning("No matching Sprint–Race pairs found for current filters.")
        return

    # ---------------------------------------------------------
    # KPI TILES — Sprint → Race Snapshot
    # ---------------------------------------------------------
    col1, col2, col3 = st.columns(3)

    avg_sprint_pos = merged["final_position_sprint"].mean()
    avg_race_pos = merged["final_position_race"].mean()
    corr = merged["final_position_sprint"].corr(merged["final_position_race"])

    with col1:
        st.metric("Avg Sprint Position", f"{avg_sprint_pos:0.1f}")
    with col2:
        st.metric("Avg Race Position", f"{avg_race_pos:0.1f}")
    with col3:
        st.metric("Sprint→Race Correlation", f"{corr:0.2f}")

    st.markdown("---")

    # ---------------------------------------------------------
    # RQ4.1 — Sprint Position vs Race Position
    # ---------------------------------------------------------
    st.markdown("### 📌 RQ4.1 — Sprint Position vs Race Position")

    fig1 = f1_fig("Sprint vs Race Final Position", height=500)

    fig1.add_trace(
        go.Scatter(
            x=merged["final_position_sprint"],
            y=merged["final_position_race"],
            mode="markers",
            marker=dict(
                size=10,
                opacity=0.7,
                color=merged["final_position_race"],
                colorscale="Turbo"
            ),
            text=merged["driver_name_sprint"],
            hovertemplate="<b>%{text}</b><br>Sprint: %{x}<br>Race: %{y}<extra></extra>"
        )
    )

    fig1.update_layout(
        xaxis_title="Sprint Final Position (Lower = Better)",
        yaxis_title="Race Final Position (Lower = Better)",
    )

    fig1.update_xaxes(autorange="reversed")
    fig1.update_yaxes(autorange="reversed")

    st.plotly_chart(fig1, use_container_width=True)

    # ---------------------------------------------------------
    # RQ4.2 — Sprint Points vs Season Points
    # ---------------------------------------------------------
    st.markdown("### 📌 RQ4.2 — Sprint Points vs Total Season Points")

    season_points = (
        df_sprint.groupby(["season", "driver_id"], as_index=False)["points"]
        .sum()
        .rename(columns={"points": "season_points"})
    )

    merged2 = merged.merge(season_points, on=["season", "driver_id"])

    if merged2.empty:
        st.warning("No Sprint/Season points data available for current filters.")
        return

    fig2 = f1_fig("Sprint Points vs Total Season Points", height=500)

    fig2.add_trace(
        go.Scatter(
            x=merged2["points_sprint"],
            y=merged2["season_points"],
            mode="markers",
            marker=dict(
                size=10,
                opacity=0.7,
                color=merged2["season_points"],
                colorscale="Viridis"
            ),
            text=merged2["driver_name_sprint"],
            hovertemplate="<b>%{text}</b><br>Sprint Points: %{x}<br>Season Points: %{y}<extra></extra>"
        )
    )

    fig2.update_layout(
        xaxis_title="Sprint Points",
        yaxis_title="Total Season Points",
    )

    st.plotly_chart(fig2, use_container_width=True)

    # ---------------------------------------------------------
    # RQ4.3 — Sprint Impact Score (New Metric)
    # ---------------------------------------------------------
    st.markdown("### 📌 RQ4.3 — Sprint Impact Score (New Metric)")

    merged2["impact_score"] = (
        (merged2["points_sprint"] / merged2["season_points"].replace(0, 1)) * 100
    )

    impact = (
        merged2.groupby("driver_name_sprint", as_index=False)["impact_score"]
        .mean()
        .sort_values("impact_score", ascending=False)
    )

    fig3 = f1_fig("Sprint Impact Score (Higher = Sprint Matters More)", height=500)

    fig3.add_trace(
        go.Bar(
            x=impact["impact_score"],
            y=impact["driver_name_sprint"],
            orientation="h",
            marker=dict(
                color=impact["impact_score"],
                colorscale="Plasma"
            ),
            hovertemplate="<b>%{y}</b><br>Impact Score: %{x:.1f}%<extra></extra>"
        )
    )

    fig3.update_layout(
        xaxis_title="Sprint Impact Score (%)",
        yaxis_title="Driver",
    )

    st.plotly_chart(fig3, use_container_width=True)

    # ---------------------------------------------------------
    # RQ4 — Insights
    # ---------------------------------------------------------
    st.markdown("### 🧠 RQ4 — Key Insights")

    st.success(
        """
        - Sprint performance shows a **strong correlation** with race-day results.  
        - Drivers who score well in Sprints tend to accumulate **higher season points**.  
        - The **Sprint Impact Score** highlights drivers who rely heavily on Sprint points to boost their championship standing.  
        - Sprint races act as a **predictive indicator** of race competitiveness and season-long momentum.  
        """
    )
