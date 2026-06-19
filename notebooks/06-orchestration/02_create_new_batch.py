import os
from pathlib import Path
import argparse
from datetime import datetime
import pandas as pd

# ------------------------------------------------------------
# Resolve WORKSPACE from CLI or env
# ------------------------------------------------------------
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=str, default=os.getenv("WORKSPACE"))
    parser.add_argument("--batch_id", type=str, required=True)
    return parser.parse_args()

args = get_args()

if not args.workspace:
    raise RuntimeError("WORKSPACE not provided. Set env var or pass --workspace.")

WORKSPACE = args.workspace.rstrip("/")
BATCH_ID = args.batch_id

BASE = WORKSPACE

# ------------------------------------------------------------
# Control table path
# ------------------------------------------------------------
CONTROL_DIR = Path(f"{BASE}/data/control")
CONTROL_DIR.mkdir(parents=True, exist_ok=True)

CONTROL_FILE = CONTROL_DIR / "batch_events.parquet"

# ------------------------------------------------------------
# Load or initialize control table
# ------------------------------------------------------------
if CONTROL_FILE.exists():
    df = pd.read_parquet(CONTROL_FILE)
else:
    df = pd.DataFrame(columns=["batch_id", "status", "created_timestamp", "updated_timestamp"])

# ------------------------------------------------------------
# Insert or update batch entry
# ------------------------------------------------------------
now = datetime.now()

# Remove any existing entry for this batch (allows reprocessing)
df = df[df["batch_id"] != BATCH_ID]

# Insert fresh entry
new_row = pd.DataFrame([{
    "batch_id": str(BATCH_ID),          # force string
    "status": "in_progress",
    "created_timestamp": now,
    "updated_timestamp": now
}])

df = pd.concat([df, new_row], ignore_index=True)

# ------------------------------------------------------------
# Save control table
# ------------------------------------------------------------
df.to_parquet(CONTROL_FILE)

print("====================================")
print("✔ Batch entry created/updated")
print(f"Batch ID: {BATCH_ID}")
print(f"Control table: {CONTROL_FILE}")
print("====================================")
