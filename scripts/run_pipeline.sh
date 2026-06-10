#!/bin/bash

# ============================================================
# RUN PIPELINE — NEW LANDING PIPELINE
# Reads from data/landing/<batch_id>
# Writes to bronze/silver/gold
# ============================================================

BASE_DIR="/Users/manoharazalki/F1-Analytics"
NB_DIR="$BASE_DIR/notebooks"
LOG_ROOT="$BASE_DIR/logs/pipeline"

BATCH_ID=$1

if [ -z "$BATCH_ID" ]; then
  echo "❌ ERROR: No batch_id provided to pipeline."
  exit 1
fi

LOG_DIR="$LOG_ROOT/$BATCH_ID"
mkdir -p "$LOG_DIR"

echo "=============================================="
echo "🚀 Running Pipeline for batch_id = $BATCH_ID"
echo "Logs: $LOG_DIR"
echo "=============================================="

# -------------------------
# Bronze
# -------------------------
papermill "$NB_DIR/02-bronze/01_ingest_circuits.ipynb" \
          "$LOG_DIR/bronze_circuits.ipynb" \
          -p p_batch_id "$BATCH_ID"

papermill "$NB_DIR/02-bronze/02_ingest_races.ipynb" \
          "$LOG_DIR/bronze_races.ipynb" \
          -p p_batch_id "$BATCH_ID"

papermill "$NB_DIR/02-bronze/03_ingest_drivers.ipynb" \
          "$LOG_DIR/bronze_drivers.ipynb" \
          -p p_batch_id "$BATCH_ID"

papermill "$NB_DIR/02-bronze/04_ingest_constructors.ipynb" \
          "$LOG_DIR/bronze_constructors.ipynb" \
          -p p_batch_id "$BATCH_ID"

papermill "$NB_DIR/02-bronze/05_ingest_results.ipynb" \
          "$LOG_DIR/bronze_results.ipynb" \
          -p p_batch_id "$BATCH_ID"

papermill "$NB_DIR/02-bronze/06_ingest_sprints.ipynb" \
          "$LOG_DIR/bronze_sprints.ipynb" \
          -p p_batch_id "$BATCH_ID"

# -------------------------
# Silver
# -------------------------
papermill "$NB_DIR/03-silver/01_transform_circuits.ipynb" \
          "$LOG_DIR/silver_circuits.ipynb" \
          -p p_batch_id "$BATCH_ID"

papermill "$NB_DIR/03-silver/02_transform_races.ipynb" \
          "$LOG_DIR/silver_races.ipynb" \
          -p p_batch_id "$BATCH_ID"

papermill "$NB_DIR/03-silver/03_transform_drivers.ipynb" \
          "$LOG_DIR/silver_drivers.ipynb" \
          -p p_batch_id "$BATCH_ID"

papermill "$NB_DIR/03-silver/04_transform_constructors.ipynb" \
          "$LOG_DIR/silver_constructors.ipynb" \
          -p p_batch_id "$BATCH_ID"

papermill "$NB_DIR/03-silver/05_transform_results.ipynb" \
          "$LOG_DIR/silver_results.ipynb" \
          -p p_batch_id "$BATCH_ID"

papermill "$NB_DIR/03-silver/06_transform_sprints.ipynb" \
          "$LOG_DIR/silver_sprints.ipynb" \
          -p p_batch_id "$BATCH_ID"

# -------------------------
# Gold
# -------------------------
papermill "$NB_DIR/04-gold/01_build_dim_races.ipynb" \
          "$LOG_DIR/gold_dim_races.ipynb" \
          -p p_batch_id "$BATCH_ID"

papermill "$NB_DIR/04-gold/02_build_dim_drivers.ipynb" \
          "$LOG_DIR/gold_dim_drivers.ipynb" \
          -p p_batch_id "$BATCH_ID"

papermill "$NB_DIR/04-gold/03_build_dim_constructors.ipynb" \
          "$LOG_DIR/gold_dim_constructors.ipynb" \
          -p p_batch_id "$BATCH_ID"

papermill "$NB_DIR/04-gold/04_build_fact_results.ipynb" \
          "$LOG_DIR/gold_fact_results.ipynb" \
          -p p_batch_id "$BATCH_ID"

echo "=============================================="
echo "🎉 Pipeline Completed for batch_id = $BATCH_ID"
echo "=============================================="
