import os
import sys
from pathlib import Path
from pyspark.sql import functions as F
from pyspark.sql import SparkSession

# ------------------------------------------------------------
# 1. Resolve WORKSPACE + BATCH_ID
# ------------------------------------------------------------
WORKSPACE = os.getenv("WORKSPACE")
BATCH_ID = os.getenv("BATCH_ID")

if not WORKSPACE:
    raise RuntimeError("WORKSPACE environment variable not set")
if not BATCH_ID:
    raise RuntimeError("BATCH_ID environment variable not set")

WORKSPACE = WORKSPACE.rstrip("/")
BASE = WORKSPACE
DATA = f"{BASE}/data"

print(f"[INFO] WORKSPACE = {WORKSPACE}")
print(f"[INFO] BATCH_ID  = {BATCH_ID}")

# ------------------------------------------------------------
# 2. Import helpers from 00-common
# ------------------------------------------------------------
COMMON = f"{BASE}/notebooks/00-common"
sys.path.append(COMMON)

from silver_helpers import write_to_silver

# ------------------------------------------------------------
# 3. Initialize Spark
# ------------------------------------------------------------
spark = (
    SparkSession.builder
        .appName(f"silver_transform_races_{BATCH_ID}")
        .config("spark.ui.enabled", "false")
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
)

# ------------------------------------------------------------
# 4. Define Bronze + Silver paths
# ------------------------------------------------------------
bronze_path = Path(f"{DATA}/bronze/races/races.parquet")
silver_dir = Path(f"{DATA}/silver/races")
silver_dir.mkdir(parents=True, exist_ok=True)

silver_output = silver_dir / "races.parquet"

print(f"[INFO] Bronze path: {bronze_path}")
print(f"[INFO] Silver path: {silver_output}")

# ------------------------------------------------------------
# 5. Read Bronze (ONLY this batch)
# ------------------------------------------------------------
races_df = (
    spark.read.parquet(str(bronze_path))
    .filter(F.col("batch_id") == BATCH_ID)
)

print("[INFO] ✔ Bronze races read")
races_df.show(5)

# ------------------------------------------------------------
# 6. Select required columns
# ------------------------------------------------------------
races_selected_df = races_df.select(
    "season",
    "round",
    "raceName",
    "date",
    "circuitId",
    "ingest_timestamp",
    "source_file",
    "batch_id"
)

# ------------------------------------------------------------
# 7. Standardize + rename columns
# ------------------------------------------------------------
races_renamed_df = (
    races_selected_df
        .withColumnRenamed("season", "year")
        .withColumnRenamed("raceName", "race_name")
        .withColumnRenamed("date", "race_date")
        .withColumnRenamed("circuitId", "circuit_id")
)

# ------------------------------------------------------------
# 8. Business key validation
# ------------------------------------------------------------
races_valid_df = races_renamed_df.filter(
    "year IS NOT NULL AND round IS NOT NULL"
)

# ------------------------------------------------------------
# 9. Remove duplicates
# ------------------------------------------------------------
races_distinct_df = races_valid_df.dropDuplicates(["year", "round"])

# ------------------------------------------------------------
# 10. Title Case transformations
# ------------------------------------------------------------
races_final_df = (
    races_distinct_df
        .withColumn("race_name", F.initcap("race_name"))
)

# ------------------------------------------------------------
# 11. Write to Silver (batch‑aware)
# ------------------------------------------------------------
write_to_silver(
    races_final_df,
    str(silver_output),
    BATCH_ID
)

print(f"[INFO] ✔ Races Silver written: {silver_output}")

# ------------------------------------------------------------
# 12. Validate
# ------------------------------------------------------------
spark.read.parquet(str(silver_output)).show(5)
