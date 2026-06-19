#!/bin/bash
set -e

# ------------------------------------------------------------
# 0. Validate args
# ------------------------------------------------------------
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "❌ ERROR: Usage: bash run_pipeline.sh <WORKSPACE> <BATCH_ID>"
    exit 1
fi

WORKSPACE="${WORKSPACE%/}"
BASE="$WORKSPACE"
export BATCH_ID="$2"
BASE="$WORKSPACE"

# ------------------------------------------------------------
# 1. Setup logs folder + log file
# ------------------------------------------------------------
SCRIPTS="$BASE/scripts"
LOG_ROOT="$SCRIPTS/logs"
PIPELINE_LOG_DIR="$LOG_ROOT/pipeline/$BATCH_ID"
mkdir -p "$PIPELINE_LOG_DIR"

TS=$(date +"%Y%m%d_%H%M%S")
MASTER_LOG="$LOG_ROOT/pipeline_${BATCH_ID}_${TS}.log"

# Redirect ALL output to log + console
exec > >(tee -a "$MASTER_LOG") 2>&1

echo "===================================="
echo "🏎️  Starting F1 Pipeline (Bronze → Silver → Gold)"
echo "===================================="
echo "✔ WORKSPACE = $WORKSPACE"
echo "✔ BATCH_ID  = $BATCH_ID"
echo "✔ MASTER LOG = $MASTER_LOG"
echo "✔ STEP LOGS  = $PIPELINE_LOG_DIR"
echo ""

# ------------------------------------------------------------
# 2. Define script paths
# ------------------------------------------------------------
BRONZE="$BASE/notebooks/02-bronze"
SILVER="$BASE/notebooks/03-silver"
GOLD="$BASE/notebooks/04-gold"

echo "✔ Using script directories:"
echo "  BRONZE = $BRONZE"
echo "  SILVER = $SILVER"
echo "  GOLD   = $GOLD"
echo ""

# ------------------------------------------------------------
# Helper: run python script with NO positional args
# ------------------------------------------------------------
run_py () {
    local script_path="$1"
    local log_path="$2"

    echo "▶ Running: $(basename "$script_path")"

    WORKSPACE="$WORKSPACE" BATCH_ID="$BATCH_ID" \
    python3 "$script_path" 2>&1 | tee "$log_path"

    echo "✔ Completed: $(basename "$script_path")"
    echo ""
}

# ------------------------------------------------------------
# 3. Bronze Layer
# ------------------------------------------------------------
echo "------------------------------------"
echo "🥉 Running BRONZE Layer"
echo "------------------------------------"

run_py "$BRONZE/01_ingest_circuits.py"      "$PIPELINE_LOG_DIR/bronze_01.log"
run_py "$BRONZE/02_ingest_races.py"         "$PIPELINE_LOG_DIR/bronze_02.log"
run_py "$BRONZE/03_ingest_drivers.py"       "$PIPELINE_LOG_DIR/bronze_03.log"
run_py "$BRONZE/04_ingest_constructors.py"  "$PIPELINE_LOG_DIR/bronze_04.log"
run_py "$BRONZE/05_ingest_results.py"       "$PIPELINE_LOG_DIR/bronze_05.log"
run_py "$BRONZE/06_ingest_sprints.py"       "$PIPELINE_LOG_DIR/bronze_06.log"

echo "✔ Bronze layer completed"
echo ""

# ------------------------------------------------------------
# 4. Silver Layer
# ------------------------------------------------------------
echo "------------------------------------"
echo "🥈 Running SILVER Layer"
echo "------------------------------------"

run_py "$SILVER/01_transform_circuits.py"      "$PIPELINE_LOG_DIR/silver_01.log"
run_py "$SILVER/02_transform_races.py"         "$PIPELINE_LOG_DIR/silver_02.log"
run_py "$SILVER/03_transform_drivers.py"       "$PIPELINE_LOG_DIR/silver_03.log"
run_py "$SILVER/04_transform_constructors.py"  "$PIPELINE_LOG_DIR/silver_04.log"
run_py "$SILVER/05_transform_results.py"       "$PIPELINE_LOG_DIR/silver_05.log"
run_py "$SILVER/06_transform_sprints.py"       "$PIPELINE_LOG_DIR/silver_06.log"

echo "✔ Silver layer completed"
echo ""

# ------------------------------------------------------------
# 5. Gold Layer
# ------------------------------------------------------------
echo "------------------------------------"
echo "🥇 Running GOLD Layer"
echo "------------------------------------"

run_py "$GOLD/01_build_dim_races.py"               "$PIPELINE_LOG_DIR/gold_01.log"
run_py "$GOLD/02_build_dim_drivers.py"             "$PIPELINE_LOG_DIR/gold_02.log"
run_py "$GOLD/03_build_dim_constructors.py"        "$PIPELINE_LOG_DIR/gold_03.log"
run_py "$GOLD/04_build_fact_session_results.py"    "$PIPELINE_LOG_DIR/gold_04.log"
run_py "$GOLD/91_build_ref_nationality_region.py"  "$PIPELINE_LOG_DIR/gold_05.log"

echo "✔ Gold layer completed"
echo ""

# ------------------------------------------------------------
# 6. Final Output
# ------------------------------------------------------------
echo "===================================="
echo "🎉 Pipeline Completed Successfully"
echo "Batch: $BATCH_ID"
echo "Step logs:   $PIPELINE_LOG_DIR"
echo "Master log:  $MASTER_LOG"
echo "===================================="
