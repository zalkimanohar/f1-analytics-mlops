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
        .appName(f"silver_transform_sprints_{BATCH_ID}")
        .config("spark.ui.enabled", "false")
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
)

# ------------------------------------------------------------
# 4. Define Bronze + Silver paths
# ------------------------------------------------------------
bronze_path = Path(f"{DATA}/bronze/sprints/sprints.parquet")
silver_dir = Path(f"{DATA}/silver/sprints")
silver_dir.mkdir(parents=True, exist_ok=True)

silver_output = silver_dir / "sprints.parquet"

print(f"[INFO] Bronze path: {bronze_path}")
print(f"[INFO] Silver path: {silver_output}")

# ------------------------------------------------------------
# 5. Read Bronze (ONLY this batch)
# ------------------------------------------------------------
sprints_df = (
    spark.read.parquet(str(bronze_path))
    .filter(F.col("batch_id") == BATCH_ID)
)

print("[INFO] ✔ Bronze sprints read")
sprints_df.show(5, truncate=False)

# ------------------------------------------------------------
# 6. Select required columns
# ------------------------------------------------------------
sprints_selected_df = sprints_df.select(
    "season",
    "round",
    "constructorId",
    "driverId",
    "raceName",
    "date",
    "grid",
    "laps",
    "number",
    "points",
    "position",
    "positionText",
    "status",
    "ingest_timestamp",
    "source_file",
    "batch_id"
)

# ------------------------------------------------------------
# 7. Standardize + rename columns
# ------------------------------------------------------------
sprints_renamed_df = (
    sprints_selected_df
        .withColumnRenamed("constructorId", "constructor_id")
        .withColumnRenamed("driverId", "driver_id")
        .withColumnRenamed("raceName", "race_name")
        .withColumnRenamed("date", "race_date")
        .withColumnRenamed("grid", "grid_position")
        .withColumnRenamed("laps", "completed_laps")
        .withColumnRenamed("number", "car_number")
        .withColumnRenamed("position", "final_position")
        .withColumnRenamed("positionText", "final_position_text")
)

# ------------------------------------------------------------
# 8. Business key validation
# ------------------------------------------------------------
sprints_valid_df = sprints_renamed_df.filter(
    "season IS NOT NULL AND round IS NOT NULL AND constructor_id IS NOT NULL AND driver_id IS NOT NULL"
)

# ------------------------------------------------------------
# 9. Remove duplicates
# ------------------------------------------------------------
sprints_distinct_df = sprints_valid_df.dropDuplicates(
    ["season", "round", "constructor_id", "driver_id"]
)

# ------------------------------------------------------------
# 10. Title Case transformations
# ------------------------------------------------------------
sprints_final_df = (
    sprints_distinct_df
        .withColumn("race_name", F.initcap("race_name"))
)

# ------------------------------------------------------------
# 11. Write to Silver (batch‑aware)
# ------------------------------------------------------------
write_to_silver(
    sprints_final_df,
    str(silver_output),
    BATCH_ID
)

print(f"[INFO] ✔ Sprints Silver written: {silver_output}")

# ------------------------------------------------------------
# 12. Validate
# ------------------------------------------------------------
spark.read.parquet(str(silver_output)).show(5, truncate=False)
