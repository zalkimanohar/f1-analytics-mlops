#!/bin/bash

echo "=============================================="
echo "🔧 Installing Workspace Dependencies (CLEAN MODE)"
echo "=============================================="

BASE="/Users/manoharazalki/F1-Analytics"
LOG_DIR="$BASE/scripts/logs"

# ---------------------------------------------------------
# 1. VERIFY PYTHON
# ---------------------------------------------------------
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Python3 not found. Install Python first."
    exit 1
else
    echo "✔ Python3 OK: $(python3 --version)"
fi

# ---------------------------------------------------------
# 2. VERIFY PIP
# ---------------------------------------------------------
if ! command -v pip3 >/dev/null 2>&1; then
    echo "❌ pip3 not found. Install pip first."
    exit 1
else
    echo "✔ pip3 OK: $(pip3 --version)"
fi

# ---------------------------------------------------------
# 3. VERIFY / INSTALL PYTHON LIBRARIES
# ---------------------------------------------------------
echo "🔍 Checking Python libraries..."

# papermill
if python3 -c "import papermill" 2>/dev/null; then
    echo "✔ papermill OK"
else
    echo "📦 Installing papermill..."
    pip3 install papermill
fi

# pyspark
if python3 -c "import pyspark" 2>/dev/null; then
    echo "✔ pyspark OK"
else
    echo "📦 Installing pyspark..."
    pip3 install pyspark
fi

# ---------------------------------------------------------
# 4. ENSURE LOGS FOLDER EXISTS (ONLY THIS FOLDER)
# ---------------------------------------------------------
if [ ! -d "$LOG_DIR" ]; then
    echo "📁 Creating logs folder..."
    mkdir -p "$LOG_DIR"
else
    echo "✔ logs folder exists"
fi

# ---------------------------------------------------------
# 5. VALIDATE WORKSPACE STRUCTURE (NO CREATION)
# ---------------------------------------------------------
echo "🔍 Validating workspace structure..."

REQUIRED_FOLDERS=(
    "$BASE/notebooks"
    "$BASE/notebooks/bronze"
    "$BASE/notebooks/silver"
    "$BASE/notebooks/gold"
    "$BASE/dashboard"
    "$BASE/scripts"
    "$BASE/data"
)

for folder in "${REQUIRED_FOLDERS[@]}"; do
    if [ -d "$folder" ]; then
        echo "✔ Found: $folder"
    else
        echo "⚠️ Missing: $folder (Not creating — CLEAN MODE)"
    fi
done

echo "=============================================="
echo "✔ Workspace Ready (NO new folders created)"
echo "=============================================="
