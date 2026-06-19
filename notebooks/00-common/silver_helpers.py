import os
from pyspark.sql import functions as F
from pyspark.sql import SparkSession

# ------------------------------------------------------------
# Resolve WORKSPACE from environment
# ------------------------------------------------------------
WORKSPACE = os.getenv("WORKSPACE")

if not WORKSPACE:
    raise RuntimeError("WORKSPACE environment variable not set")

WORKSPACE = WORKSPACE.rstrip("/")
BASE = WORKSPACE
DATA = f"{BASE}/data"

print(f"[INFO] silver_helpers WORKSPACE = {WORKSPACE}")

# ------------------------------------------------------------
# Initialize Spark (for reading existing Silver files if needed)
# ------------------------------------------------------------
spark = (
    SparkSession.builder
        .appName("F1-Analytics-Silver")
        .config("spark.ui.enabled", "false")
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
)

# ------------------------------------------------------------
# Silver Helper Function (Batch-Aware)
# ------------------------------------------------------------
def write_to_silver(df, output_path: str, batch_id: str):
    """
    Writes Silver data for a specific batch_id.
    Each write is isolated for that batch_id.
    """
    df = (
        df.withColumn("batch_id", F.lit(batch_id))
          .withColumn("created_timestamp", F.current_timestamp())
          .withColumn("updated_timestamp", F.current_timestamp())
    )

    (
        df.write
          .mode("overwrite")
          .parquet(output_path)
    )

print("[INFO] silver_helpers loaded successfully.")
