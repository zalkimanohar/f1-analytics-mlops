# dashboard/sections/rq3_circuit_geography.py

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import f1_fig

def render_rq3(df: pd.DataFrame):
    st.markdown("## 🟩 RQ3 — CIRCUIT & GEOGRAPHICAL PERFORMANCE")

    if df.empty:
        st.info("No data available for current filters in RQ3.")
        return

    # ---------------------------------------------------------
    # FIX: unify nationality_region column
    # ---------------------------------------------------------
    if "nationality_region" not in df.columns:
        if "nationality_region_x" in df.columns:
            df["nationality_region"] = df["nationality_region_x"]
        elif "nationality_region_y" in df.columns:
            df["nationality_region"] = df["nationality_region_y"]
        else:
            df["nationality_region"] = "Other"

    # ---------------------------------------------------------
    # KPI TILES — GEOGRAPHICAL SNAPSHOT
    # ---------------------------------------------------------
    col1, col2, col3 = st.columns(3)

    avg_points = df["points"].mean()
    top_country = (
        df.groupby("country_name")["points"]
        .mean()
        .sort_values(ascending=False)
        .index[0]
    )
    top_circuit = (
        df.groupby("circuit_name")["points"]
        .mean()
        .sort_values(ascending=False)
        .index[0]
    )

    with col1:
        st.metric("Avg Points per Race", f"{avg_points:0.2f}")
    with col2:
        st.metric("Top Performing Country", top_country)
    with col3:
        st.metric("Top Performing Circuit", top_circuit)

    st.markdown("---")

    # ---------------------------------------------------------
    # RQ3.1 — Circuit Competitiveness Index (Std Dev of Points)
    # ---------------------------------------------------------
    st.markdown("### 📌 RQ3.1 — Circuit Competitiveness Index")

    circuit_comp = (
        df.groupby("circuit_name")["points"]
        .std()
        .reset_index()
        .rename(columns={"points": "points_std"})
        .sort_values("points_std", ascending=False)
    )

    fig1 = f1_fig("Circuit Competitiveness Index (Higher = More Variable)", height=500)

    fig1.add_trace(
        go.Bar(
            x=circuit_comp["circuit_name"].head(20),
            y=circuit_comp["points_std"].head(20),
            marker=dict(
                color=px.colors.qualitative.Dark24[:len(circuit_comp.head(20))]
            ),
            hovertemplate="<b>%{x}</b><br>Std Dev: %{y:.2f}<extra></extra>"
        )
    )

    fig1.update_layout(
        xaxis_title="Circuit",
        yaxis_title="Points Standard Deviation",
        xaxis_tickangle=-45
    )

    st.plotly_chart(fig1, use_container_width=True)

    # ---------------------------------------------------------
    # RQ3.2 — Country Performance (Avg Points)
    # ---------------------------------------------------------
    st.markdown("### 📌 RQ3.2 — Average Points by Host Country")

    country_perf = (
        df.groupby("country_name", as_index=False)["points"]
        .mean()
        .sort_values("points", ascending=False)
    )

    fig2 = f1_fig("Average Points by Host Country", height=500)

    fig2.add_trace(
        go.Bar(
            x=country_perf["country_name"],
            y=country_perf["points"],
            marker=dict(
                color=px.colors.qualitative.Set3[:len(country_perf)]
            ),
            hovertemplate="<b>%{x}</b><br>Avg Points: %{y:.2f}<extra></extra>"
        )
    )

    fig2.update_layout(
        xaxis_title="Country",
        yaxis_title="Average Points",
        xaxis_tickangle=-45
    )

    st.plotly_chart(fig2, use_container_width=True)

    # ---------------------------------------------------------
    # RQ3.3 — Driver Region vs Performance
    # ---------------------------------------------------------
    st.markdown("### 📌 RQ3.3 — Driver Region vs Performance")

    region_perf = (
        df.groupby("nationality_region", as_index=False)["points"]
        .mean()
        .sort_values("points", ascending=False)
    )

    fig3 = f1_fig("Driver Region vs Performance", height=450)

    fig3.add_trace(
        go.Bar(
            x=region_perf["nationality_region"],
            y=region_perf["points"],
            marker=dict(
                color=px.colors.qualitative.Pastel[:len(region_perf)]
            ),
            hovertemplate="<b>%{x}</b><br>Avg Points: %{y:.2f}<extra></extra>"
        )
    )

    fig3.update_layout(
        xaxis_title="Region",
        yaxis_title="Average Points",
    )

    st.plotly_chart(fig3, use_container_width=True)

    # ---------------------------------------------------------
    # RQ3.4 — Geographic Map of Race Performance
    # ---------------------------------------------------------
    st.markdown("### 🌍 RQ3.4 — Geographic Map of Race Performance")

    if "latitude" in df.columns and "longitude" in df.columns:
        map_df = (
            df.groupby(["country_name", "latitude", "longitude"], as_index=False)["points"]
            .mean()
        )

        fig4 = px.scatter_geo(
            map_df,
            lat="latitude",
            lon="longitude",
            color="country_name",
            hover_name="country_name",
            size="points",
            projection="natural earth",
            color_discrete_sequence=px.colors.qualitative.Bold,
            title="Average Points by Country (Geographical View)"
        )

        fig4.update_layout(
            template="plotly_dark",
            height=550,
        )

        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Geographical coordinates not available for map visualization.")

    # ---------------------------------------------------------
    # RQ3 — Insights
    # ---------------------------------------------------------
    st.markdown("### 🧠 RQ3 — Key Insights")

    st.success(
        """
        - Circuits with **high competitiveness index** tend to produce unpredictable race outcomes.  
        - Certain countries consistently yield **higher average points**, indicating track familiarity or car suitability.  
        - Driver regions show clear performance clusters — some regions outperform others across seasons.  
        - The **geographical map** highlights global hotspots of strong race performance.  
        """
    )
