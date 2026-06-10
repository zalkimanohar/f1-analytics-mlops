#!/bin/bash

# ============================================================
# MAIN ORCHESTRATOR — NEW LANDING PIPELINE
# Detects batch_id from data/landing/<batch_id>
# Runs orchestration → pipeline → dashboard
# ============================================================

BASE_DIR="/Users/manoharazalki/F1-Analytics"
SCRIPT_DIR="$BASE_DIR/scripts"
LANDING_DIR="$BASE_DIR/data/landing"

echo "=============================================="
echo "🏎️  Starting MAIN Pipeline Execution"
echo "=============================================="

# -----------------------------------------
# 1. Detect latest batch folder
# -----------------------------------------
echo "🔍 Detecting latest batch in: $LANDING_DIR"

LATEST_BATCH=$(ls -1t "$LANDING_DIR" | head -n 1)

if [ -z "$LATEST_BATCH" ]; then
  echo "❌ ERROR: No batch folders found in $LANDING_DIR"
  exit 1
fi

echo "➡ Detected batch_id: $LATEST_BATCH"

# -----------------------------------------
# 2. Run Orchestration
# -----------------------------------------
bash "$SCRIPT_DIR/run_orchestration.sh" "$LATEST_BATCH"

# -----------------------------------------
# 3. Run Pipeline
# -----------------------------------------
bash "$SCRIPT_DIR/run_pipeline.sh" "$LATEST_BATCH"

# -----------------------------------------
# 4. Start Dashboard
# -----------------------------------------
bash "$SCRIPT_DIR/run_dashboard.sh"

echo "=============================================="
echo "🎉 MAIN Pipeline Completed Successfully"
echo "=============================================="
