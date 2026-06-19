import os
import sys
from pathlib import Path
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
sys.path.append(f"{BASE}/notebooks/00-common")
from bronze_helpers import add_ingestion_metadata, write_to_bronze

# ------------------------------------------------------------
# 3. Paths (corrected)
# ------------------------------------------------------------
LANDING_BATCH_DIR = Path(f"{DATA}/landing/{BATCH_ID}/results")

# dynamic filename: results_2025.json
source_file = next(LANDING_BATCH_DIR.glob("results_*.json"))

BRONZE_DIR = Path(f"{DATA}/bronze/results")
BRONZE_DIR.mkdir(parents=True, exist_ok=True)

target_path = BRONZE_DIR / "results.parquet"

print(f"[INFO] Source file: {source_file}")
print(f"[INFO] Target path: {target_path}")

# ------------------------------------------------------------
# 4. Spark
# ------------------------------------------------------------
spark = (
    SparkSession.builder
        .appName(f"bronze_ingest_results_{BATCH_ID}")
        .config("spark.ui.enabled", "false")
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
)

# ------------------------------------------------------------
# 5. Read JSON (multiline-safe)
# ------------------------------------------------------------
df = (
    spark.read
        .format("json")
        .option("multiline", True)
        .load(str(source_file))
)

print("[INFO] ✔ Results file read successfully")

# ------------------------------------------------------------
# 6. Metadata + Write
# ------------------------------------------------------------
df_final = add_ingestion_metadata(df, str(source_file))
write_to_bronze(df_final, str(target_path), BATCH_ID)

print(f"[INFO] ✔ Results Bronze written to: {target_path}")

# ------------------------------------------------------------
# 7. Validate
# ------------------------------------------------------------
spark.read.parquet(str(target_path)).show(5, truncate=False)
