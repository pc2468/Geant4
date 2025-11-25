#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 1. Load dependency logic
if [ -f "$SCRIPT_DIR/dependencies.sh" ]; then
  # shellcheck source=/dev/null
  source "$SCRIPT_DIR/dependencies.sh"
else
  echo "ERROR: dependencies.sh not found in $SCRIPT_DIR"
  exit 1
fi

# 2. Install everything needed (Python, git, build tools, venv, pip deps)
install_all_deps

# at this point we assume:
# - geant4_env venv exists
# - it's activated
# - requests + colorama are installed

# 3. Download geant4_install.py if missing
if [ ! -f geant4_install.py ]; then
  echo "Downloading geant4_install.py..."
  curl -fsSL -o geant4_install.py \
    https://raw.githubusercontent.com/pc2468/Geant4/main/geant4_install.py || {
      echo "Failed to download geant4_install.py. Please check the URL."
      deactivate || true
      exit 1
    }
fi

echo "Running Geant4 installation script..."
python geant4_install.py

deactivate || true
echo "Geant4 installation script finished."
