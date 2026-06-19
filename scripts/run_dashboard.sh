#!/bin/bash
set -e

# ------------------------------------------------------------
# 1. Parse arguments
# ------------------------------------------------------------
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --workspace)
            WORKSPACE="$2"
            shift 2
            ;;
        *)
            echo "❌ Unknown parameter: $1"
            echo "Usage: ./run_dashboard.sh --workspace <path>"
            exit 1
            ;;
    esac
done

if [ -z "$WORKSPACE" ]; then
    echo "❌ ERROR: WORKSPACE not provided."
    echo "Usage: ./run_dashboard.sh --workspace <path>"
    exit 1
fi

WORKSPACE="${WORKSPACE%/}"

# ------------------------------------------------------------
# 2. Resolve project root
# ------------------------------------------------------------
# If user passed parent folder → append F1-Analytics
if [ -d "$WORKSPACE/F1-Analytics/dashboard" ]; then
    PROJECT_ROOT="$WORKSPACE/F1-Analytics"
else
    PROJECT_ROOT="$WORKSPACE"
fi

DASHBOARD_DIR="$PROJECT_ROOT/dashboard"
SCRIPTS="$PROJECT_ROOT/scripts"
LOG_DIR="$SCRIPTS/logs"

mkdir -p "$LOG_DIR"

# ------------------------------------------------------------
# 3. Create log file
# ------------------------------------------------------------
TS=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/dashboard_$TS.log"

# Redirect ALL output to log + console
exec > >(tee -a "$LOG_FILE") 2>&1

echo "=============================================="
echo "🏎️ F1 Analytics — DASHBOARD LAUNCHER"
echo "=============================================="
echo "✔ WORKSPACE     = $WORKSPACE"
echo "✔ PROJECT ROOT  = $PROJECT_ROOT"
echo "✔ DASHBOARD DIR = $DASHBOARD_DIR"
echo "✔ LOG FILE      = $LOG_FILE"
echo ""

# ------------------------------------------------------------
# 4. Launch Streamlit
# ------------------------------------------------------------
cd "$DASHBOARD_DIR"

echo "🚀 Launching Streamlit Dashboard..."
streamlit run app.py

echo ""
echo "=============================================="
echo "🎉 Dashboard exited"
echo "Log saved at: $LOG_FILE"
echo "=============================================="
