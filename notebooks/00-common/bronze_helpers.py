import os
from pyspark.sql import functions as F

# ------------------------------------------------------------
# Resolve WORKSPACE
# ------------------------------------------------------------
WORKSPACE = os.getenv("WORKSPACE")

if not WORKSPACE:
    raise RuntimeError("WORKSPACE environment variable not set")

WORKSPACE = WORKSPACE.rstrip("/")
BASE = WORKSPACE
DATA = f"{BASE}/data"

print(f"[INFO] bronze_helpers WORKSPACE = {WORKSPACE}")

# ------------------------------------------------------------
# Bronze Helper Functions
# ------------------------------------------------------------
def add_ingestion_metadata(df, source_path: str):
    return (
        df.withColumn("ingest_timestamp", F.current_timestamp())
          .withColumn("source_file", F.lit(source_path))
    )

def write_to_bronze(df, output_path: str, batch_id: str):
    (
        df.withColumn("batch_id", F.lit(batch_id))
          .write
          .mode("overwrite")
          .parquet(output_path)
    )

print("[INFO] bronze_helpers loaded successfully.")
