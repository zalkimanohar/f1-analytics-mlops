# dashboard/sections/rq5_cross_dataset.py

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import f1_fig

def render_rq5(df: pd.DataFrame):
    st.markdown("## 🟧 RQ5 — ADVANCED CROSS‑DATASET INSIGHTS")

    if df.empty:
        st.info("No data available for current filters in RQ5.")
        return

    # ---------------------------------------------------------
    # KPI TILES — CROSS‑DATASET SNAPSHOT
    # ---------------------------------------------------------
    col1, col2, col3 = st.columns(3)

    avg_points = df["points"].mean()
    top_driver = df.groupby("driver_name")["points"].mean().idxmax()
    top_constructor = df.groupby("constructor_name")["points"].mean().idxmax()

    with col1:
        st.metric("Avg Points per Entry", f"{avg_points:0.2f}")
    with col2:
        st.metric("Top Driver (Avg Points)", top_driver)
    with col3:
        st.metric("Top Constructor (Avg Points)", top_constructor)

    st.markdown("---")

    # ---------------------------------------------------------
    # RQ5.1 — Driver × Constructor × Circuit Heatmap
    # ---------------------------------------------------------
    st.markdown("### 📌 RQ5.1 — Driver × Constructor × Circuit Heatmap")

    heat = (
        df.groupby(["driver_name", "constructor_name", "circuit_name"], as_index=False)["points"]
        .mean()
    )

    if not heat.empty:
        fig1 = px.density_heatmap(
            heat,
            x="constructor_name",
            y="driver_name",
            z="points",
            color_continuous_scale="Turbo",
            title="Driver × Constructor × Circuit (Avg Points)",
        )

        fig1.update_layout(
            template="plotly_dark",
            height=600,
            xaxis_title="Constructor",
            yaxis_title="Driver",
        )

        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("No heatmap data available for current filters.")

    # ---------------------------------------------------------
    # RQ5.2 — Season Trend Lines (Constructor Points)
    # ---------------------------------------------------------
    st.markdown("### 📌 RQ5.2 — Season Trend Lines (Constructor Points)")

    season_trend = (
        df.groupby(["season", "constructor_name"], as_index=False)["points"]
        .sum()
    )

    if not season_trend.empty:
        fig2 = f1_fig("Constructor Season Trend Lines", height=500)

        for constructor in season_trend["constructor_name"].unique():
            sub = season_trend[season_trend["constructor_name"] == constructor]
            fig2.add_trace(
                go.Scatter(
                    x=sub["season"],
                    y=sub["points"],
                    mode="lines+markers",
                    name=constructor,
                    hovertemplate="<b>%{x}</b><br>Points: %{y}<extra></extra>"
                )
            )

        fig2.update_layout(
            xaxis_title="Season",
            yaxis_title="Total Points",
        )

        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No season trend data available.")

    # ---------------------------------------------------------
    # RQ5.3 — Constructor–Driver Synergy Score
    # ---------------------------------------------------------
    st.markdown("### 📌 RQ5.3 — Constructor–Driver Synergy Score")

    synergy = (
        df.groupby(["driver_name", "constructor_name"], as_index=False)["points"]
        .mean()
        .rename(columns={"points": "synergy_score"})
        .sort_values("synergy_score", ascending=False)
    )

    fig3 = f1_fig("Constructor–Driver Synergy Score", height=550)

    fig3.add_trace(
        go.Bar(
            x=synergy["synergy_score"].head(20),
            y=synergy["driver_name"].head(20),
            orientation="h",
            marker=dict(
                color=synergy["synergy_score"].head(20),
                colorscale="Viridis"
            ),
            hovertemplate="<b>%{y}</b><br>Synergy Score: %{x:.2f}<extra></extra>"
        )
    )

    fig3.update_layout(
        xaxis_title="Avg Points Together",
        yaxis_title="Driver",
    )

    st.plotly_chart(fig3, use_container_width=True)

    # ---------------------------------------------------------
    # RQ5.4 — Circuit Difficulty Index
    # ---------------------------------------------------------
    st.markdown("### 📌 RQ5.4 — Circuit Difficulty Index")

    difficulty = (
        df.groupby("circuit_name")["final_position"]
        .std()
        .reset_index()
        .rename(columns={"final_position": "difficulty_index"})
        .sort_values("difficulty_index", ascending=False)
    )

    fig4 = f1_fig("Circuit Difficulty Index (Higher = More Variable Outcomes)", height=550)

    fig4.add_trace(
        go.Bar(
            x=difficulty["difficulty_index"].head(20),
            y=difficulty["circuit_name"].head(20),
            orientation="h",
            marker=dict(
                color=difficulty["difficulty_index"].head(20),
                colorscale="Plasma"
            ),
            hovertemplate="<b>%{y}</b><br>Difficulty Index: %{x:.2f}<extra></extra>"
        )
    )

    fig4.update_layout(
        xaxis_title="Difficulty Index (Std Dev of Final Position)",
        yaxis_title="Circuit",
    )

    st.plotly_chart(fig4, use_container_width=True)

    # ---------------------------------------------------------
    # RQ5 — Insights
    # ---------------------------------------------------------
    st.markdown("### 🧠 RQ5 — Key Insights")

    st.success(
        """
        - The **Driver × Constructor × Circuit heatmap** reveals performance hotspots and weak combinations.  
        - Season trend lines highlight constructors with **consistent year‑on‑year improvement**.  
        - The **Synergy Score** identifies driver–constructor pairings that extract maximum performance together.  
        - The **Circuit Difficulty Index** shows which tracks produce unpredictable outcomes.  
        - RQ5 ties together all datasets to uncover **deep, multi‑layered performance patterns**.  
        """
    )
