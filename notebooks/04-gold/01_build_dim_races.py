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
# 2. Import helpers
# ------------------------------------------------------------
COMMON = f"{BASE}/notebooks/00-common"
sys.path.append(COMMON)
from gold_helpers import write_to_gold

# ------------------------------------------------------------
# 3. Initialize Spark
# ------------------------------------------------------------
spark = (
    SparkSession.builder
        .appName(f"gold_dim_races_{BATCH_ID}")
        .config("spark.ui.enabled", "false")
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
)

# ------------------------------------------------------------
# 4. Define Silver + Gold paths
# ------------------------------------------------------------
silver_races_path = Path(f"{DATA}/silver/races/races.parquet")
silver_circuits_path = Path(f"{DATA}/silver/circuits/circuits.parquet")

gold_output = f"{DATA}/gold/dim_races/dim_races"   # gold_helpers adds .parquet

print(f"[INFO] Silver races:    {silver_races_path}")
print(f"[INFO] Silver circuits: {silver_circuits_path}")
print(f"[INFO] Gold output:     {gold_output}.parquet")

# ------------------------------------------------------------
# 5. Read Silver (ONLY this batch)
# ------------------------------------------------------------
races_df = (
    spark.read.parquet(str(silver_races_path))
    .filter(F.col("batch_id") == BATCH_ID)
)

circuits_df = (
    spark.read.parquet(str(silver_circuits_path))
    .filter(F.col("batch_id") == BATCH_ID)
)

print("[INFO] ✔ Silver races read")
print("[INFO] ✔ Silver circuits read")

# ------------------------------------------------------------
# 6. Join races + circuits (FIXED: include circuit_id)
# ------------------------------------------------------------
dim_races_df = (
    races_df.alias("r")
        .join(
            circuits_df.alias("c"),
            F.col("r.circuit_id") == F.col("c.circuit_id"),
            "left"
        )
        .select(
            F.col("r.year").alias("season"),
            F.col("r.round"),
            F.col("r.race_name"),
            F.col("r.race_date"),
            F.col("r.circuit_id"),              # ⭐ REQUIRED FOR DASHBOARD
            F.col("c.circuit_name"),
            F.col("c.locality"),
            F.col("c.country_name").alias("country")
        )
)

# ------------------------------------------------------------
# 7. Business key validation
# ------------------------------------------------------------
dim_races_valid = dim_races_df.filter(
    "season IS NOT NULL AND round IS NOT NULL"
)

# ------------------------------------------------------------
# 8. Deduplicate
# ------------------------------------------------------------
dim_races_final = dim_races_valid.dropDuplicates(["season", "round"])

# ------------------------------------------------------------
# 9. Write to Gold (correct signature)
# ------------------------------------------------------------
write_to_gold(
    dim_races_final,
    gold_output,
    ["season", "round"]
)

print(f"[INFO] ✔ dim_races written to: {gold_output}.parquet")

# ------------------------------------------------------------
# 10. Validate
# ------------------------------------------------------------
spark.read.parquet(f"{gold_output}.parquet").show(5, truncate=False)
