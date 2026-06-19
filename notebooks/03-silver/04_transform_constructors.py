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
        .appName(f"silver_transform_constructors_{BATCH_ID}")
        .config("spark.ui.enabled", "false")
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
)

# ------------------------------------------------------------
# 4. Define Bronze + Silver paths
# ------------------------------------------------------------
bronze_path = Path(f"{DATA}/bronze/constructors/constructors.parquet")
silver_dir = Path(f"{DATA}/silver/constructors")
silver_dir.mkdir(parents=True, exist_ok=True)

silver_output = silver_dir / "constructors.parquet"

print(f"[INFO] Bronze path: {bronze_path}")
print(f"[INFO] Silver path: {silver_output}")

# ------------------------------------------------------------
# 5. Read Bronze (ONLY this batch)
# ------------------------------------------------------------
constructors_df = (
    spark.read.parquet(str(bronze_path))
    .filter(F.col("batch_id") == BATCH_ID)
)

print("[INFO] ✔ Bronze constructors read")
constructors_df.show(5, truncate=False)

# ------------------------------------------------------------
# 6. Select required columns
# ------------------------------------------------------------
constructors_selected_df = constructors_df.select(
    "constructorId",
    "name",
    "nationality",
    "url",
    "ingest_timestamp",
    "source_file",
    "batch_id"
)

# ------------------------------------------------------------
# 7. Standardize + rename columns
# ------------------------------------------------------------
constructors_renamed_df = (
    constructors_selected_df
        .withColumnRenamed("constructorId", "constructor_id")
        .withColumnRenamed("name", "constructor_name")
)

# ------------------------------------------------------------
# 8. Business key validation
# ------------------------------------------------------------
constructors_valid_df = constructors_renamed_df.filter(
    "constructor_id IS NOT NULL"
)

# ------------------------------------------------------------
# 9. Remove duplicates
# ------------------------------------------------------------
constructors_distinct_df = constructors_valid_df.dropDuplicates(["constructor_id"])

# ------------------------------------------------------------
# 10. Title Case transformations
# ------------------------------------------------------------
constructors_final_df = (
    constructors_distinct_df
        .withColumn("constructor_name", F.initcap("constructor_name"))
        .withColumn("nationality", F.initcap("nationality"))
)

# ------------------------------------------------------------
# 11. Write to Silver (batch‑aware)
# ------------------------------------------------------------
write_to_silver(
    constructors_final_df,
    str(silver_output),
    BATCH_ID
)

print(f"[INFO] ✔ Constructors Silver written: {silver_output}")

# ------------------------------------------------------------
# 12. Validate
# ------------------------------------------------------------
spark.read.parquet(str(silver_output)).show(5, truncate=False)
