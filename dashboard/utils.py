import os
import pandas as pd
import plotly.graph_objects as go

# ---------------------------------------------------------
# WORKSPACE-AWARE BASE PATH
# ---------------------------------------------------------
DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(DASHBOARD_DIR, ".."))

BASE = os.path.join(PROJECT_ROOT, "data")

# ---------------------------------------------------------
# GOLD TABLE LOADER (FIXED)
# ---------------------------------------------------------
def load_gold(table: str) -> pd.DataFrame:
    mapping = {
        "drivers": f"{BASE}/gold/dim_drivers/dim_drivers.parquet",
        "constructors": f"{BASE}/gold/dim_constructors/dim_constructors.parquet",
        "races": f"{BASE}/gold/dim_races/dim_races.parquet",
        # FIXED: correct fact table path
        "results": f"{BASE}/gold/fact_session_results/fact_session_results.parquet",
        "nationality": f"{BASE}/gold/ref_nationality_region/ref_nationality_region.parquet",
    }

    if table not in mapping:
        print(f"⚠ Unknown GOLD table requested: {table}")
        return pd.DataFrame()

    path = mapping[table]

    if not os.path.exists(path):
        print(f"⚠ Missing GOLD file: {path}")
        return pd.DataFrame()

    df = pd.read_parquet(path)

    # ---------------------------------------------------------
    # COLUMN NORMALIZATION FOR DASHBOARD COMPATIBILITY
    # ---------------------------------------------------------
    rename_map = {
        # Races
        "year": "season",
        "race_name": "race_name",
        "race_date": "race_date",

        # Results
        "grid": "grid_position",
        "position": "final_position",
    }

    df = df.rename(columns=rename_map)

    return df

# ---------------------------------------------------------
# SILVER TABLE LOADER
# ---------------------------------------------------------
def load_silver(table: str) -> pd.DataFrame:
    mapping = {
        "circuits": f"{BASE}/silver/circuits/circuits.parquet",
        "sprints": f"{BASE}/silver/sprints/sprints.parquet",
    }

    if table not in mapping:
        print(f"⚠ Unknown SILVER table requested: {table}")
        return pd.DataFrame()

    path = mapping[table]

    if not os.path.exists(path):
        print(f"⚠ Missing SILVER file: {path}")
        return pd.DataFrame()

    return pd.read_parquet(path)

# ---------------------------------------------------------
# UNIFIED LOADER
# ---------------------------------------------------------
def load_table(table: str) -> pd.DataFrame:
    gold_tables = ["drivers", "constructors", "races", "results", "nationality"]
    if table in gold_tables:
        return load_gold(table)

    silver_tables = ["circuits", "sprints"]
    if table in silver_tables:
        return load_silver(table)

    print(f"⚠ Unknown table requested: {table}")
    return pd.DataFrame()

# ---------------------------------------------------------
# STANDARD F1 FIGURE TEMPLATE
# ---------------------------------------------------------
def f1_fig(title=""):
    fig = go.Figure()
    fig.update_layout(
        title=title,
        template="plotly_dark",
        paper_bgcolor="#0d0d0d",
        plot_bgcolor="#0d0d0d",
        font=dict(color="#e6e6e6", size=14),
        title_font=dict(color="#ff1e00", size=22),
        margin=dict(l=40, r=40, t=80, b=40),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="#333333",
            borderwidth=1
        )
    )
    return fig
