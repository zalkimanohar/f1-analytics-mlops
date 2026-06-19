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
        .appName(f"silver_transform_circuits_{BATCH_ID}")
        .config("spark.ui.enabled", "false")
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
)

# ------------------------------------------------------------
# 4. Define Bronze + Silver paths
# ------------------------------------------------------------
bronze_path = Path(f"{DATA}/bronze/circuits/circuits.parquet")
silver_dir = Path(f"{DATA}/silver/circuits")
silver_dir.mkdir(parents=True, exist_ok=True)

silver_output = silver_dir / "circuits.parquet"

print(f"[INFO] Bronze path: {bronze_path}")
print(f"[INFO] Silver path: {silver_output}")

# ------------------------------------------------------------
# 5. Read Bronze (ONLY this batch)
# ------------------------------------------------------------
circuits_df = (
    spark.read.parquet(str(bronze_path))
    .filter(F.col("batch_id") == BATCH_ID)
)

print("[INFO] ✔ Bronze circuits read")
circuits_df.show(5)

# ------------------------------------------------------------
# 6. Select required columns
# ------------------------------------------------------------
circuits_selected_df = circuits_df.select(
    "circuitId",
    "circuitName",
    "lat",
    "long",
    "locality",
    "country",
    "ingest_timestamp",
    "source_file",
    "batch_id"
)

# ------------------------------------------------------------
# 7. Standardize + rename columns
# ------------------------------------------------------------
circuits_renamed_df = (
    circuits_selected_df
        .withColumnRenamed("circuitId", "circuit_id")
        .withColumnRenamed("circuitName", "circuit_name")
        .withColumnRenamed("lat", "latitude")
        .withColumnRenamed("long", "longitude")
)

# ------------------------------------------------------------
# 8. Business key validation
# ------------------------------------------------------------
circuits_valid_df = circuits_renamed_df.filter("circuit_id IS NOT NULL")

# ------------------------------------------------------------
# 9. Remove duplicates
# ------------------------------------------------------------
circuits_distinct_df = circuits_valid_df.dropDuplicates(["circuit_id"])

# ------------------------------------------------------------
# 10. Title Case transformations
# ------------------------------------------------------------
circuits_final_df = (
    circuits_distinct_df
        .withColumn("circuit_name", F.initcap("circuit_name"))
        .withColumn("locality", F.initcap("locality"))
        .withColumnRenamed("country", "country_name")
)

# ------------------------------------------------------------
# 11. Write to Silver (batch‑aware)
# ------------------------------------------------------------
write_to_silver(
    circuits_final_df,
    str(silver_output),
    BATCH_ID
)

print(f"[INFO] ✔ Circuits Silver written: {silver_output}")

# ------------------------------------------------------------
# 12. Validate
# ------------------------------------------------------------
spark.read.parquet(str(silver_output)).show(5)
