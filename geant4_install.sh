#!/bin/bash
set -e

# Always work in a new "Geant4" folder in the directory where the user runs the script
INSTALL_DIR="$PWD/Geant4"

# Create it if it doesn't exist
mkdir -p "$INSTALL_DIR"

# Move into it
cd "$INSTALL_DIR"

# 1. Load dependencies.sh (local if present, otherwise download from repo)
if [ -f "dependencies.sh" ]; then
  source "dependencies.sh"
else
  echo "dependencies.sh not found, downloading from repo..."
  curl -fsSL -o dependencies.sh \
    https://raw.githubusercontent.com/pc2468/Geant4/main/dependencies.sh \
    || { echo "Failed to download dependencies.sh"; exit 1; }
  source "dependencies.sh"
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
