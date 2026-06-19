import os
from pathlib import Path
from datetime import datetime
from pyspark.sql import SparkSession

# ------------------------------------------------------------
# 1. Resolve WORKSPACE from environment
# ------------------------------------------------------------
WORKSPACE = os.getenv("WORKSPACE")

if not WORKSPACE:
    raise RuntimeError("WORKSPACE environment variable not set")

WORKSPACE = WORKSPACE.rstrip("/")
BASE = WORKSPACE
DATA = f"{BASE}/data"

print(f"[INFO] WORKSPACE = {WORKSPACE}")
print(f"[INFO] DATA PATH = {DATA}")

# ------------------------------------------------------------
# 2. Initialize Spark Session
# ------------------------------------------------------------
spark = (
    SparkSession.builder
        .appName("F1-Analytics")
        .config("spark.ui.enabled", "false")
        .config("spark.ui.showConsoleProgress", "false")
        .config("spark.sql.shuffle.partitions", "200")
        .getOrCreate()
)

# ------------------------------------------------------------
# 3. Define Base Paths (NO folder creation here)
# ------------------------------------------------------------
LANDING_PATH     = f"{DATA}/landing"
BRONZE_PATH      = f"{DATA}/bronze"
SILVER_PATH      = f"{DATA}/silver"
GOLD_PATH        = f"{DATA}/gold"
INCREMENTAL_PATH = f"{DATA}/incremental"
CONTROL_PATH     = f"{DATA}/control"

# ------------------------------------------------------------
# 4. Path Helpers
# ------------------------------------------------------------
def bronze_path(table_name: str):
    return f"{BRONZE_PATH}/{table_name}"

def silver_path(table_name: str):
    return f"{SILVER_PATH}/{table_name}"

def gold_path(table_name: str):
    return f"{GOLD_PATH}/{table_name}"

def incremental_path(batch_folder: str):
    return f"{INCREMENTAL_PATH}/{batch_folder}"

# ------------------------------------------------------------
# 5. Detect Latest Batch ID (landing folder)
# ------------------------------------------------------------
def detect_latest_batch_id():
    landing_dir = Path(LANDING_PATH)

    if not landing_dir.exists():
        return None

    batch_folders = [
        f.name for f in landing_dir.iterdir()
        if f.is_dir() and f.name != "events"
    ]

    if not batch_folders:
        return None

    return sorted(batch_folders)[-1]

p_batch_id = detect_latest_batch_id()

print("===== F1 Analytics Environment Configuration =====")
print(f"LANDING_PATH:     {LANDING_PATH}")
print(f"BRONZE_PATH:      {BRONZE_PATH}")
print(f"SILVER_PATH:      {SILVER_PATH}")
print(f"GOLD_PATH:        {GOLD_PATH}")
print(f"INCREMENTAL_PATH: {INCREMENTAL_PATH}")
print(f"CONTROL_PATH:     {CONTROL_PATH}")
print(f"p_batch_id:       {p_batch_id}")
print("===================================================")
