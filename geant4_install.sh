#!/bin/bash
set -e

# Detect the directory of this script if it exists on disk.
# If running via curl, fall back to current working directory.
if [[ -n "${BASH_SOURCE[0]}" && -f "${BASH_SOURCE[0]}" ]]; then
  SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &>/dev/null && pwd )"
else
  SCRIPT_DIR="$PWD"
fi

cd "$SCRIPT_DIR"

# 1. Load dependencies.sh (local if present, otherwise download from your repo)
if [ -f "$SCRIPT_DIR/dependencies.sh" ]; then
  source "$SCRIPT_DIR/dependencies.sh"
else
  echo "dependencies.sh not found locally, downloading from repo..."
  curl -fsSL -o /tmp/dependencies.sh \
    https://raw.githubusercontent.com/pc2468/Geant4/main/dependencies.sh \
    || { echo "Failed to download dependencies.sh"; exit 1; }
  source /tmp/dependencies.sh
fi

# 2. Install all dependencies
install_all_deps

# 3. Download geant4_install.py if missing
if [ ! -f geant4_install.py ]; then
  echo "Downloading geant4_install.py..."
  curl -fsSL -o geant4_install.py \
    https://raw.githubusercontent.com/pc2468/Geant4/main/geant4_install.py \
    || { echo "Failed to download geant4_install.py"; exit 1; }
fi

echo "Running Geant4 installation script..."
python geant4_install.py

deactivate || true
echo "Geant4 installation script finished."
