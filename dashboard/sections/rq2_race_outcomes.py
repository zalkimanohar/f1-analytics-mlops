# dashboard/sections/rq2_race_outcomes.py

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import f1_fig

def render_rq2(df: pd.DataFrame):
    st.markdown("## 🟦 RQ2 — RACE EXECUTION & OUTCOME DRIVERS")

    if df.empty:
        st.info("No data available for current filters in RQ2.")
        return

    # ---------------------------------------------------------
    # KPI TILES — EXECUTION SNAPSHOT
    # ---------------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)

    avg_grid = df["grid_position"].mean()
    avg_final = df["final_position"].mean()
    avg_gain = df["positions_gained"].mean()

    dnf_mask = df["status"].str.contains("DNF", case=False, na=False)
    dnf_rate_overall = dnf_mask.mean() * 100

    with col1:
        st.metric("Avg Grid Position", f"{avg_grid:0.1f}")
    with col2:
        st.metric("Avg Final Position", f"{avg_final:0.1f}")
    with col3:
        st.metric("Avg Positions Gained", f"{avg_gain:0.2f}")
    with col4:
        st.metric("DNF Rate", f"{dnf_rate_overall:0.1f}%")

    st.markdown("---")

    # ---------------------------------------------------------
    # RQ2.1 — Grid vs Final Position (Scatter)
    # ---------------------------------------------------------
    st.markdown("### 📌 RQ2.1 — Grid vs Final Position")

    fig_scatter = px.scatter(
        df,
        x="grid_position",
        y="final_position",
        color="driver_name",
        title="Grid vs Final Position (Lower is Better)",
        opacity=0.65,
        hover_data=["season", "round", "race_name", "constructor_name", "points"],
        color_discrete_sequence=px.colors.qualitative.Dark24
    )

    fig_scatter.update_layout(
        template="plotly_dark",
        height=500,
        legend_title="Driver",
        xaxis_title="Grid Position (Start)",
        yaxis_title="Final Position (Finish)",
    )
    fig_scatter.update_yaxes(autorange="reversed")

    st.plotly_chart(fig_scatter, use_container_width=True)

    # ---------------------------------------------------------
    # RQ2.2 — Constructor DNF Rate (Bar)
    # ---------------------------------------------------------
    st.markdown("### 📌 RQ2.2 — Constructor DNF Rate")

    dnf_rate = (
        df.assign(is_dnf=dnf_mask)
        .groupby("constructor_name", as_index=False)["is_dnf"]
        .mean()
        .rename(columns={"is_dnf": "dnf_rate"})
    )

    dnf_rate["dnf_rate_pct"] = dnf_rate["dnf_rate"] * 100
    dnf_rate = dnf_rate.sort_values("dnf_rate_pct", ascending=False)

    fig_dnf = px.bar(
        dnf_rate,
        x="constructor_name",
        y="dnf_rate_pct",
        title="Constructor DNF Rate (%)",
        color="constructor_name",
        color_discrete_sequence=px.colors.qualitative.Set3,
        labels={"dnf_rate_pct": "DNF Rate (%)", "constructor_name": "Constructor"},
    )

    fig_dnf.update_layout(
        template="plotly_dark",
        height=450,
        xaxis_tickangle=-45,
    )

    st.plotly_chart(fig_dnf, use_container_width=True)

    # ---------------------------------------------------------
    # RQ2.3 — Driver Recovery Index (Avg Positions Gained)
    # ---------------------------------------------------------
    st.markdown("### 📌 RQ2.3 — Driver Recovery Index")

    recovery = (
        df.groupby("driver_name", as_index=False)["positions_gained"]
        .mean()
        .sort_values("positions_gained", ascending=False)
    )

    fig_recovery = px.bar(
        recovery,
        x="positions_gained",
        y="driver_name",
        orientation="h",
        title="Average Positions Gained from Grid to Finish",
        color="driver_name",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        labels={"positions_gained": "Avg Positions Gained", "driver_name": "Driver"},
    )

    fig_recovery.update_layout(
        template="plotly_dark",
        height=600,
    )

    st.plotly_chart(fig_recovery, use_container_width=True)

    # ---------------------------------------------------------
    # RQ2 — Insights
    # ---------------------------------------------------------
    st.markdown("### 🧠 RQ2 — Key Execution Insights")

    st.success(
        """
        - **Grid vs Final Position** highlights drivers and teams that consistently convert strong starts into strong finishes.  
        - **Constructor DNF Rate** surfaces reliability risk—high DNF constructors may need engineering or strategy focus.  
        - **Driver Recovery Index** identifies overtaking specialists who gain positions regardless of starting slot.  
        """
    )
