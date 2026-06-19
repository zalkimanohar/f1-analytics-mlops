import os
from pathlib import Path

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
# 2. Define required folder structure (MUST match your tree)
# ------------------------------------------------------------
REQUIRED_DIRS = [
    f"{DATA}/landing",
    f"{DATA}/landing/events",
    f"{DATA}/bronze",
    f"{DATA}/silver",
    f"{DATA}/gold",
    f"{DATA}/incremental",
    f"{DATA}/control",
]

# ------------------------------------------------------------
# 3. Create directories safely (NO duplicates)
# ------------------------------------------------------------
for d in REQUIRED_DIRS:
    Path(d).mkdir(parents=True, exist_ok=True)

print("✔ All required project directories are ready.")

# ------------------------------------------------------------
# 4. Print Summary
# ------------------------------------------------------------
print("===== F1 Analytics Project Environment Setup =====")
for d in REQUIRED_DIRS:
    print(f"✔ {d}")
print("==================================================")
