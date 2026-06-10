#!/bin/bash

# ============================================================
# RUN ORCHESTRATION — NEW LANDING PIPELINE
# Uses p_batch_id passed from main.sh
# ============================================================

BASE_DIR="/Users/manoharazalki/F1-Analytics"
NB_DIR="$BASE_DIR/notebooks/06-orchestration"
LOG_DIR="$BASE_DIR/logs/orchestration"

mkdir -p "$LOG_DIR"

BATCH_ID=$1

if [ -z "$BATCH_ID" ]; then
  echo "❌ ERROR: No batch_id provided to orchestration."
  exit 1
fi

echo "=============================================="
echo "🔧 Running Orchestration for batch_id = $BATCH_ID"
echo "=============================================="

# -----------------------------------------
# 1. Create Batch Entry
# -----------------------------------------
papermill "$NB_DIR/02.Create New Batch.ipynb" \
          "$LOG_DIR/create_batch_$BATCH_ID.ipynb" \
          -p p_batch_id "$BATCH_ID"

# -----------------------------------------
# 2. Mark Batch as Identified
# -----------------------------------------
papermill "$NB_DIR/01.Identify Next Batch.ipynb" \
          "$LOG_DIR/identify_batch_$BATCH_ID.ipynb" \
          -p p_batch_id "$BATCH_ID"

# -----------------------------------------
# 3. Complete Batch
# -----------------------------------------
papermill "$NB_DIR/03.Complete Batch.ipynb" \
          "$LOG_DIR/complete_batch_$BATCH_ID.ipynb" \
          -p p_batch_id "$BATCH_ID"

echo "=============================================="
echo "✔ Orchestration Completed"
echo "=============================================="
