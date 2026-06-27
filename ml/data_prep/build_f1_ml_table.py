import pandas as pd
from pathlib import Path

BASE = Path("/Users/manoharazalki/F1-Analytics")
GOLD = BASE / "data" / "gold"
OUTPUT = BASE / "data" / "ml" / "f1_driver_race.parquet"

def drop_metadata(df):
    """Remove duplicate metadata columns to avoid merge conflicts."""
    cols_to_drop = ["batch_id", "created_timestamp", "updated_timestamp"]
    return df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors="ignore")

def build_f1_ml_table():
    print("Loading GOLD tables...")

    dim_drivers = drop_metadata(pd.read_parquet(GOLD / "dim_drivers" / "dim_drivers.parquet"))
    dim_constructors = drop_metadata(pd.read_parquet(GOLD / "dim_constructors" / "dim_constructors.parquet"))
    dim_races = drop_metadata(pd.read_parquet(GOLD / "dim_races" / "dim_races.parquet"))
    fact_results = drop_metadata(pd.read_parquet(GOLD / "fact_session_results" / "fact_session_results.parquet"))
    ref_region = drop_metadata(pd.read_parquet(GOLD / "ref_nationality_region" / "ref_nationality_region.parquet"))

    print("Joining tables using season + round...")

    df = (
        fact_results
        .merge(dim_drivers, on="driver_id", how="left")
        .merge(dim_constructors, on="constructor_id", how="left")
        .merge(dim_races, on=["season", "round"], how="left")
        .merge(ref_region, left_on="driver_nationality", right_on="nationality", how="left")
    )

    print("Creating labels...")

    df["is_podium"] = (df["final_position"] <= 3).astype(int)
    df["is_winner"] = (df["final_position"] == 1).astype(int)

    print(f"Saving ML dataset to {OUTPUT}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUTPUT, index=False)

    print("ML dataset created successfully!")

if __name__ == "__main__":
    build_f1_ml_table()
