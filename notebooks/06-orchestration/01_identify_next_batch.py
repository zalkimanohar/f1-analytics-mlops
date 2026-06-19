import os
from pathlib import Path
import argparse

# ------------------------------------------------------------
# Resolve WORKSPACE from environment or CLI
# ------------------------------------------------------------
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
# Paths
# ------------------------------------------------------------
LANDING_ROOT = Path(f"{BASE}/data/landing")

# ------------------------------------------------------------
# Helper: detect latest batch folder
# ------------------------------------------------------------
def get_latest_batch_id():
    """
    Detects the latest batch folder inside data/landing.
    Folder names follow YYYY-MM format: 2025-01, 2025-02, ...
    This version:
    - Ignores .ready files
    - Ignores control table
    - Always picks the latest folder
    - Returns None only if landing is empty
    """
    if not LANDING_ROOT.exists():
        raise RuntimeError(f"Landing folder missing: {LANDING_ROOT}")

    # List only directories like 2025-01, 2025-02, ...
    batch_folders = sorted([
        d.name for d in LANDING_ROOT.iterdir()
        if d.is_dir()
    ])

    if not batch_folders:
        return None

    return batch_folders[-1]  # newest folder


# ------------------------------------------------------------
# Main logic
# ------------------------------------------------------------
p_batch_id = get_latest_batch_id()

if p_batch_id is None:
    print("p_batch_id None")
    print("has_batch false")
    exit(0)

# Always treat latest batch as valid
print(f"p_batch_id {p_batch_id}")
print("has_batch true")
