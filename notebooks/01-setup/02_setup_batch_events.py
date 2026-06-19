import os
from pathlib import Path
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, TimestampType

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
# 2. Define paths
# ------------------------------------------------------------
CONTROL_DIR = Path(f"{DATA}/control")
CONTROL_TABLE = CONTROL_DIR / "batch_events.parquet"

EVENTS_DIR = Path(f"{DATA}/landing/events")
READY_FLAG = EVENTS_DIR / f"{BATCH_ID}.ready"

# ------------------------------------------------------------
# 3. Ensure required folders exist
# ------------------------------------------------------------
CONTROL_DIR.mkdir(parents=True, exist_ok=True)
EVENTS_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------
# 4. Initialize Spark
# ------------------------------------------------------------
spark = (
    SparkSession.builder
        .appName("F1-Analytics-Setup-Batch-Events")
        .config("spark.ui.enabled", "false")
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
)

# ------------------------------------------------------------
# 5. Create control table if missing
# ------------------------------------------------------------
schema = StructType([
    StructField("batch_id", StringType(), True),
    StructField("event_timestamp", TimestampType(), True)
])

if not CONTROL_TABLE.exists():
    empty_df = spark.createDataFrame([], schema)
    empty_df.write.mode("overwrite").parquet(str(CONTROL_TABLE))
    print("✔ Created batch_events.parquet")
else:
    print("✔ batch_events.parquet already exists")

# ------------------------------------------------------------
# 6. Insert batch event (append)
# ------------------------------------------------------------
new_event = spark.createDataFrame(
    [(BATCH_ID, datetime.utcnow())],
    ["batch_id", "event_timestamp"]
)

existing = spark.read.parquet(str(CONTROL_TABLE))
final_df = existing.unionByName(new_event)

final_df.write.mode("overwrite").parquet(str(CONTROL_TABLE))

print(f"✔ Inserted batch event for {BATCH_ID}")

# ------------------------------------------------------------
# 7. Create READY flag
# ------------------------------------------------------------
if not READY_FLAG.exists():
    READY_FLAG.touch()
    print(f"✔ Created READY flag: {READY_FLAG}")
else:
    print(f"✔ READY flag already exists: {READY_FLAG}")

print("====================================")
print("✔ Batch Events Setup Complete")
print("====================================")
