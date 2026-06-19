import os
import glob
import shutil
from pathlib import Path
from pyspark.sql import functions as F
from pyspark.sql import SparkSession

# ------------------------------------------------------------
# Resolve WORKSPACE + BATCH_ID
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

print(f"[INFO] gold_helpers WORKSPACE = {WORKSPACE}")
print(f"[INFO] gold_helpers BATCH_ID  = {BATCH_ID}")

# ------------------------------------------------------------
# Initialize Spark
# ------------------------------------------------------------
spark = (
    SparkSession.builder
        .appName("F1-Analytics-Gold")
        .config("spark.ui.enabled", "false")
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
)

# ------------------------------------------------------------
# SAFE GOLD MERGE + SINGLE PARQUET WRITER
# ------------------------------------------------------------
def write_to_gold(df, output_path: str, merge_keys: list):
    """
    SAFE GOLD MERGE:
    - Reads existing table (if exists)
    - Adds batch_id + timestamps
    - Deduplicates using merge_keys
    - Writes a SINGLE parquet file (no Spark folders)
    """

    # Add metadata
    df = (
        df.withColumn("batch_id", F.lit(BATCH_ID))
          .withColumn("created_timestamp", F.current_timestamp())
          .withColumn("updated_timestamp", F.current_timestamp())
    )

    final_path = output_path + ".parquet"
    final_path_obj = Path(final_path)

    # ------------------------------------------------------------
    # Merge with existing Gold table if present
    # ------------------------------------------------------------
    if final_path_obj.exists():
        print(f"[INFO] Existing Gold table found → merging: {final_path}")
        existing_df = spark.read.parquet(final_path)

        merged_df = (
            existing_df.unionByName(df, allowMissingColumns=True)
                       .dropDuplicates(merge_keys)
        )
    else:
        print(f"[INFO] Creating new Gold table: {final_path}")
        merged_df = df

    # ------------------------------------------------------------
    # Write to temporary Spark folder
    # ------------------------------------------------------------
    tmp_dir = output_path + "_tmp"

    # Clean old tmp if exists
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir, ignore_errors=True)

    merged_df.coalesce(1).write.mode("overwrite").parquet(tmp_dir)

    # ------------------------------------------------------------
    # Move part file → final single parquet
    # ------------------------------------------------------------
    part_files = glob.glob(f"{tmp_dir}/part-*.parquet")
    if not part_files:
        raise RuntimeError(f"No part file written for {output_path}")

    part_file = part_files[0]

    # ------------------------------------------------------------
    # Remove old final file OR folder
    # ------------------------------------------------------------
    if final_path_obj.exists():
        if final_path_obj.is_dir():
            shutil.rmtree(final_path, ignore_errors=True)
        else:
            final_path_obj.unlink()

    # Ensure parent directory exists
    os.makedirs(os.path.dirname(final_path), exist_ok=True)

    # Move the new single parquet file
    shutil.move(part_file, final_path)

    # Cleanup tmp folder
    shutil.rmtree(tmp_dir, ignore_errors=True)

    print(f"[INFO] Gold table written: {final_path}")
