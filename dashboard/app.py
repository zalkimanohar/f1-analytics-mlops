import streamlit as st
from utils import load_f1_gold

from sections.rq1_driver_constructor import render_rq1
from sections.rq2_race_outcomes import render_rq2
from sections.rq3_circuit_geography import render_rq3
from sections.rq4_sprint_race import render_rq4
from sections.rq5_cross_dataset import render_rq5
from sections.executive_summary import render_summary


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="F1 Performance Intelligence Dashboard",
    page_icon="🏎️",
    layout="wide"
)

st.title("🏎️ F1 PERFORMANCE INTELLIGENCE DASHBOARD")
st.markdown("_A Multi-Layered Analysis of Drivers, Constructors, Circuits & Strategy (RQ1–RQ5)_")


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
@st.cache_data
def get_data():
    return load_f1_gold()

df = get_data()


# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------
with st.sidebar:
    st.header("🎛️ Global Filters")

    # -------------------------------
    # QUICK SEASON SELECTOR
    # -------------------------------
    st.markdown("### Quick Season Filters")

    quick = st.radio(
        "Select Range",
        ["Last 5 Seasons", "Last 10 Seasons", "All Seasons"],
        horizontal=True
    )

    all_seasons = sorted(df["season"].unique(), reverse=True)

    if quick == "Last 5 Seasons":
        default_seasons = all_seasons[:5]
    elif quick == "Last 10 Seasons":
        default_seasons = all_seasons[:10]
    else:
        default_seasons = all_seasons

    # -------------------------------
    # SEASON MULTISELECT
    # -------------------------------
    seasons = st.multiselect(
        "Season (Descending Order)",
        all_seasons,
        default=default_seasons,
        placeholder="Select Seasons"
    )

    # -------------------------------
    # TOP 10 DRIVERS DEFAULT
    # -------------------------------
    top_drivers = (
        df.groupby("driver_name")["points"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .index
    )

    drivers = st.multiselect(
        "Driver",
        sorted(df["driver_name"].unique()),
        default=top_drivers
    )

    constructors = st.multiselect(
        "Constructor",
        sorted(df["constructor_name"].unique())
    )

    circuits = st.multiselect(
        "Circuit",
        sorted(df["circuit_name"].dropna().unique())
    )

    final_pos = st.slider(
        "Final Position",
        int(df["final_position"].min()),
        int(df["final_position"].max()),
        (int(df["final_position"].min()), int(df["final_position"].max()))
    )

    grid_pos = st.slider(
        "Grid Position",
        int(df["grid_position"].min()),
        int(df["grid_position"].max()),
        (int(df["grid_position"].min()), int(df["grid_position"].max()))
    )

    points_range = st.slider(
        "Points",
        float(df["points"].min()),
        float(df["points"].max()),
        (float(df["points"].min()), float(df["points"].max()))
    )

    status = st.multiselect(
        "Status (DNF/Finished)",
        sorted(df["status"].unique())
    )


# ---------------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------------
filtered = df[df["season"].isin(seasons)]

if circuits:
    filtered = filtered[filtered["circuit_name"].isin(circuits)]

if drivers:
    filtered = filtered[filtered["driver_name"].isin(drivers)]

if constructors:
    filtered = filtered[filtered["constructor_name"].isin(constructors)]

filtered = filtered[
    (filtered["final_position"].between(*final_pos)) &
    (filtered["grid_position"].between(*grid_pos)) &
    (filtered["points"].between(*points_range))
]

if status:
    filtered = filtered[filtered["status"].isin(status)]


# ---------------------------------------------------------
# RENDER SECTIONS
# ---------------------------------------------------------
render_rq1(filtered)
render_rq2(filtered)
render_rq3(filtered)
render_rq4(filtered)
render_rq5(filtered)
render_summary()
