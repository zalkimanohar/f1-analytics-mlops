import os
import sys
from pathlib import Path
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, DateType
)
from pyspark.sql import SparkSession

# ------------------------------------------------------------
# 1. Resolve WORKSPACE + BATCH_ID from environment
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
# 2. Fix Python import path for 00-common helpers
# ------------------------------------------------------------
sys.path.append(f"{BASE}/notebooks/00-common")

from bronze_helpers import (
    add_ingestion_metadata,
    write_to_bronze
)

# ------------------------------------------------------------
# 3. Define landing + bronze paths
# ------------------------------------------------------------
LANDING_BATCH_DIR = Path(f"{DATA}/landing/{BATCH_ID}")

BRONZE_DIR = Path(f"{DATA}/bronze/races")
BRONZE_DIR.mkdir(parents=True, exist_ok=True)

source_file = LANDING_BATCH_DIR / "races.csv"
target_path = BRONZE_DIR / "races.parquet"

print(f"[INFO] Source file: {source_file}")
print(f"[INFO] Target path: {target_path}")

# ------------------------------------------------------------
# 4. Initialize Spark
# ------------------------------------------------------------
spark = (
    SparkSession.builder
        .appName(f"bronze_ingest_races_{BATCH_ID}")
        .config("spark.ui.enabled", "false")
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
)

# ------------------------------------------------------------
# 5. Validate landing file
# ------------------------------------------------------------
if not source_file.exists():
    raise RuntimeError(f"Landing file not found: {source_file}")

# ------------------------------------------------------------
# 6. Schema
# ------------------------------------------------------------
races_schema = StructType([
    StructField('season', IntegerType(), True),
    StructField('round', IntegerType(), True),
    StructField('url', StringType(), True),
    StructField('raceName', StringType(), True),
    StructField('date', DateType(), True),
    StructField('circuitId', StringType(), True)
])

# ------------------------------------------------------------
# 7. Read CSV
# ------------------------------------------------------------
races_df = (
    spark.read
        .format("csv")
        .schema(races_schema)
        .option("header", True)
        .option("mode", "FAILFAST")
        .load(str(source_file))
)

print("[INFO] ✔ Races file read successfully")

# ------------------------------------------------------------
# 8. Add ingestion metadata
# ------------------------------------------------------------
races_final_df = add_ingestion_metadata(races_df, str(source_file))

print("[INFO] ✔ Metadata added")

# ------------------------------------------------------------
# 9. Write to Bronze
# ------------------------------------------------------------
write_to_bronze(
    races_final_df,
    str(target_path),
    BATCH_ID
)

print(f"[INFO] ✔ Races Bronze written to: {target_path}")

# ------------------------------------------------------------
# 10. Validate
# ------------------------------------------------------------
print("[INFO] Showing sample from Bronze output:")
spark.read.parquet(str(target_path)).show(5)
