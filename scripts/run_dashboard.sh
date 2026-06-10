#!/bin/bash

# ============================================================
# RUN STREAMLIT DASHBOARD
# ============================================================

BASE_DIR="/Users/manoharazalki/F1-Analytics"
APP_PATH="$BASE_DIR/dashboard/app.py"
LOG_FILE="$BASE_DIR/logs/dashboard.log"
VENV_PATH="$BASE_DIR/f1env/bin/activate"

echo "=============================================="
echo "📊 Starting Dashboard"
echo "=============================================="

# Activate venv
source "$VENV_PATH"

# Clear cache
streamlit cache clear

# Run dashboard
streamlit run "$APP_PATH" 2>&1 | tee "$LOG_FILE"
