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
        .appName(f"gold_dim_constructors_{BATCH_ID}")
        .config("spark.ui.enabled", "false")
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
)

# ------------------------------------------------------------
# 4. Define Silver + Gold paths
# ------------------------------------------------------------
silver_constructors_path = Path(f"{DATA}/silver/constructors/constructors.parquet")

gold_output = f"{DATA}/gold/dim_constructors/dim_constructors"   # gold_helpers adds .parquet

print(f"[INFO] Silver constructors: {silver_constructors_path}")
print(f"[INFO] Gold output:         {gold_output}.parquet")

# ------------------------------------------------------------
# 5. Read Silver (ONLY this batch)
# ------------------------------------------------------------
constructors_df = (
    spark.read.parquet(str(silver_constructors_path))
    .filter(F.col("batch_id") == BATCH_ID)
)

print("[INFO] ✔ Silver constructors read")

# ------------------------------------------------------------
# 6. Select required columns
# ------------------------------------------------------------
dim_constructors_df = (
    constructors_df.select(
        F.col("constructor_id"),
        F.col("constructor_name"),
        F.col("nationality"),
        F.col("url")
    )
)

# ------------------------------------------------------------
# 7. Business key validation
# ------------------------------------------------------------
dim_constructors_valid = dim_constructors_df.filter("constructor_id IS NOT NULL")

# ------------------------------------------------------------
# 8. Deduplicate
# ------------------------------------------------------------
dim_constructors_final = dim_constructors_valid.dropDuplicates(["constructor_id"])

# ------------------------------------------------------------
# 9. Write to Gold (correct signature)
# ------------------------------------------------------------
write_to_gold(
    dim_constructors_final,
    gold_output,
    ["constructor_id"]
)

print(f"[INFO] ✔ dim_constructors written to: {gold_output}.parquet")

# ------------------------------------------------------------
# 10. Validate
# ------------------------------------------------------------
spark.read.parquet(f"{gold_output}.parquet").show(5, truncate=False)
