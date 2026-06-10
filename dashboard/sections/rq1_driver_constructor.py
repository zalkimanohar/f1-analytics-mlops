# dashboard/sections/rq1_driver_constructor.py

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from utils import f1_fig

def render_rq1(df):
    st.markdown("## 🟥 RQ1 — DRIVER & CONSTRUCTOR PERFORMANCE")

    # ============================================================
    # RQ1.1 — Driver Season Performance (Line Chart)
    # ============================================================
    st.markdown("### 📌 RQ1.1 — Driver Season Performance")

    driver_season = (
        df.groupby(["season", "driver_name"], as_index=False)["points"]
        .sum()
    )

    fig1 = f1_fig("Driver Season Performance", height=450)

    # Unique colour per driver using Plotly's automatic palette
    for driver in driver_season["driver_name"].unique():
        sub = driver_season[driver_season["driver_name"] == driver]
        fig1.add_trace(
            go.Scatter(
                x=sub["season"],
                y=sub["points"],
                mode="lines+markers",
                name=driver,
                hovertemplate="<b>%{x}</b><br>Points: %{y}<extra></extra>"
            )
        )

    fig1.update_layout(
        xaxis_title="Season",
        yaxis_title="Total Points",
    )

    st.plotly_chart(fig1, use_container_width=True)

    # ============================================================
    # RQ1.2 — Constructor Season Performance (Stacked Bar)
    # ============================================================
    st.markdown("### 📌 RQ1.2 — Constructor Season Performance")

    constructor_season = (
        df.groupby(["season", "constructor_name"], as_index=False)["points"]
        .sum()
    )

    fig2 = f1_fig("Constructor Season Performance (Stacked)", height=450)

    # Unique colour per constructor
    for constructor in constructor_season["constructor_name"].unique():
        sub = constructor_season[constructor_season["constructor_name"] == constructor]
        fig2.add_trace(
            go.Bar(
                x=sub["season"],
                y=sub["points"],
                name=constructor,
                hovertemplate="<b>%{x}</b><br>Points: %{y}<extra></extra>"
            )
        )

    fig2.update_layout(
        barmode="stack",
        xaxis_title="Season",
        yaxis_title="Total Points",
    )

    st.plotly_chart(fig2, use_container_width=True)

    # ============================================================
    # RQ1.3 — Driver Consistency Index (Lower = Better)
    # ============================================================
    st.markdown("### 📌 RQ1.3 — Driver Consistency Index")

    consistency = (
        df.groupby("driver_name", as_index=False)["final_position"]
        .std()
        .rename(columns={"final_position": "position_std"})
        .sort_values("position_std")
    )

    fig3 = f1_fig("Driver Consistency Index (Lower = More Consistent)", height=500)

    fig3.add_trace(
        go.Bar(
            x=consistency["position_std"],
            y=consistency["driver_name"],
            orientation="h",
            marker=dict(
                color=consistency["position_std"],
                colorscale="Bluered"
            ),
            hovertemplate="<b>%{y}</b><br>Std Dev: %{x:.2f}<extra></extra>"
        )
    )

    fig3.update_layout(
        xaxis_title="Position Standard Deviation",
        yaxis_title="Driver",
    )

    st.plotly_chart(fig3, use_container_width=True)

    # ============================================================
    # RQ1.4 — Driver Age vs Points (Scatter)
    # ============================================================
    st.markdown("### 📌 RQ1.4 — Driver Age vs Points")

    fig4 = f1_fig("Driver Age vs Points", height=500)

    fig4.add_trace(
        go.Scatter(
            x=df["age_at_race"],
            y=df["points"],
            mode="markers",
            marker=dict(
                size=9,
                opacity=0.7,
                color=df["points"],
                colorscale="Turbo"
            ),
            text=df["driver_name"],
            hovertemplate="<b>%{text}</b><br>Age: %{x:.1f}<br>Points: %{y}<extra></extra>"
        )
    )

    fig4.update_layout(
        xaxis_title="Age at Race",
        yaxis_title="Points",
    )

    st.plotly_chart(fig4, use_container_width=True)

    # ============================================================
    # RQ1.5 — Constructor Dominance (Standings Table)
    # ============================================================
    st.markdown("### 📌 RQ1.5 — Constructor Dominance (Standings)")

    standings = (
        df.groupby(["season", "constructor_name"], as_index=False)["points"]
        .sum()
        .sort_values(["season", "points"], ascending=[True, False])
    )

    st.dataframe(standings, use_container_width=True)

    # ---------------------------------------------------------
    # RQ1 — Insights
    # ---------------------------------------------------------
    st.markdown("### 🧠 RQ1 — Key Execution Insights")

    st.success(
        """
        **Driver Performance**
        - Drivers with consistently high season points demonstrate strong adaptability across circuits and conditions.
        - Line‑chart trends reveal momentum shifts — drivers who peak mid‑season often correlate with car upgrades or strategic improvements.
        - Large fluctuations in season points highlight drivers affected by reliability issues or inconsistent qualifying performance.

        **Constructor Performance**
        - Constructors with stacked season bars show engineering stability and strong race‑day execution.
        - Teams with rising year‑on‑year points indicate successful development cycles and operational maturity.
        - Constructors with volatile season totals often face reliability challenges or inconsistent driver pairings.

        **Driver Consistency Index**
        - Low standard deviation in finishing positions indicates elite consistency — these drivers maximize points even on bad weekends.
        - High variability suggests aggressive driving styles, risk‑heavy strategies, or machinery instability.

        **Age vs Performance**
        - Younger drivers show higher volatility but occasional peak performances.
        - Experienced drivers maintain stable scoring patterns, reflecting racecraft maturity and strategic discipline.

        **Overall RQ1 Insight**
        - RQ1 reveals the foundational performance pillars: driver skill, constructor engineering strength, and season‑long consistency.
        """
    )
