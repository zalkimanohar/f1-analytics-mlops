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
COMMON = f"{BASE}/notebooks/00-common"
sys.path.append(COMMON)
from gold_helpers import write_to_gold

# ------------------------------------------------------------
# 3. Initialize Spark
# ------------------------------------------------------------
spark = (
    SparkSession.builder
        .appName("gold_ref_nationality_region")
        .config("spark.ui.enabled", "false")
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
)

# ------------------------------------------------------------
# 4. Define output path
# ------------------------------------------------------------
gold_output = f"{DATA}/gold/ref_nationality_region/ref_nationality_region"

print(f"[INFO] Gold output: {gold_output}.parquet")

# ------------------------------------------------------------
# 5. Static mapping table
# ------------------------------------------------------------
data = [
    ("British", "Europe"),
    ("German", "Europe"),
    ("Spanish", "Europe"),
    ("French", "Europe"),
    ("Italian", "Europe"),
    ("Dutch", "Europe"),
    ("Finnish", "Europe"),
    ("Danish", "Europe"),
    ("Swiss", "Europe"),
    ("Austrian", "Europe"),
    ("Belgian", "Europe"),
    ("Swedish", "Europe"),
    ("Australian", "Oceania"),
    ("New Zealander", "Oceania"),
    ("American", "North America"),
    ("Canadian", "North America"),
    ("Mexican", "North America"),
    ("Brazilian", "South America"),
    ("Argentine", "South America"),
    ("Japanese", "Asia"),
    ("Chinese", "Asia"),
    ("Indian", "Asia"),
    ("Thai", "Asia"),
    ("South African", "Africa"),
]

columns = ["nationality", "region"]

df = spark.createDataFrame(data, columns)

# ------------------------------------------------------------
# 6. Write to Gold (single parquet, merge-safe)
# ------------------------------------------------------------
write_to_gold(
    df,
    gold_output,
    ["nationality"]
)

print(f"[INFO] ✔ ref_nationality_region written to: {gold_output}.parquet")

# ------------------------------------------------------------
# 7. Validate
# ------------------------------------------------------------
spark.read.parquet(f"{gold_output}.parquet").show(20, truncate=False)
