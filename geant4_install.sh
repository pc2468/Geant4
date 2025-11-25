#!/bin/bash
set -e

# Figure out script directory; fall back to $PWD when run via curl
if [[ -n "${BASH_SOURCE[0]}" && "${BASH_SOURCE[0]}" != "bash" && "${BASH_SOURCE[0]}" != "-bash" ]]; then
  SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
else
  SCRIPT_DIR="$PWD"
fi

cd "$SCRIPT_DIR"

# 1. Load dependency logic (local if present, otherwise from GitHub)
if [ -f "$SCRIPT_DIR/dependencies.sh" ]; then
  # shellcheck source=/dev/null
  source "$SCRIPT_DIR/dependencies.sh"
else
  echo "dependencies.sh not found in $SCRIPT_DIR, downloading temporary copy..."
  TMP_DEPS="/tmp/geant4_dependencies.sh"
  curl -fsSL -o "$TMP_DEPS" \
    https://raw.githubusercontent.com/pc2468/Geant4/main/dependencies.sh || {
      echo "Failed to download dependencies.sh. Aborting."
      exit 1
    }
  # shellcheck source=/dev/null
  source "$TMP_DEPS"
fi

# 2. Install everything needed (Python, git, build tools, venv, pip deps)
install_all_deps

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
