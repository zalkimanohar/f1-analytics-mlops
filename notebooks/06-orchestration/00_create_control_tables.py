import os
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType, StructField,
    StringType, TimestampType
)

# ------------------------------------------------------------
# Resolve WORKSPACE from environment or CLI
# ------------------------------------------------------------
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=str, default=os.getenv("WORKSPACE"))
    return parser.parse_args()

args = get_args()

if not args.workspace:
    raise RuntimeError("WORKSPACE not provided. Set env var or pass --workspace.")

WORKSPACE = args.workspace.rstrip("/")
BASE = WORKSPACE  # BASE == F1-Analytics root

# ------------------------------------------------------------
# Control table path (must match your folder tree)
# ------------------------------------------------------------
CONTROL_DIR = Path(f"{BASE}/data/control")
CONTROL_TABLE = CONTROL_DIR / "batch_events.parquet"

# ------------------------------------------------------------
# Create control directory (safe, no duplicates)
# ------------------------------------------------------------
CONTROL_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------
# Initialize Spark
# ------------------------------------------------------------
spark = SparkSession.builder.appName("create_control_table").getOrCreate()

# ------------------------------------------------------------
# Create empty control table ONLY IF missing
# ------------------------------------------------------------
if not CONTROL_TABLE.exists():
    print("[INFO] Control table missing — creating new batch_events.parquet")

    schema = StructType([
        StructField("batch_id",          StringType(), True),
        StructField("status",            StringType(), True),
        StructField("created_timestamp", TimestampType(), True),
        StructField("updated_timestamp", TimestampType(), True),
    ])

    empty_df = spark.createDataFrame([], schema)
    empty_df.write.mode("overwrite").parquet(str(CONTROL_TABLE))

else:
    print("[INFO] Control table already exists — not modifying it")

# ------------------------------------------------------------
# Validation output
# ------------------------------------------------------------
print("====================================")
print("✔ Control table ready")
print(f"Directory: {CONTROL_DIR}")
print(f"Table:     {CONTROL_TABLE}")
print("====================================")
