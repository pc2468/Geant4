#!/usr/bin/env bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

is_installed() {
  dpkg-query -l "$1" &>/dev/null || \
  rpm -q "$1" &>/dev/null || \
  pacman -Qs "$1" &>/dev/null || \
  zypper se -i "$1" &>/dev/null
}

get_installed_python_version() {
  python3 --version 2>&1 | awk '{print $2}'
}

update_python3() {
  echo "Updating Python3..."
  if [ -x "$(command -v apt-get)" ]; then
    sudo apt-get update && sudo apt-get install --only-upgrade python3 -y
  elif [ -x "$(command -v dnf)" ]; then
    sudo dnf upgrade python3 -y
  elif [ -x "$(command -v pacman)" ]; then
    sudo pacman -Syu python --noconfirm
  elif [ -x "$(command -v zypper)" ]; then
    sudo zypper update python3 -y
  else
    echo "Unsupported package manager. Please update Python3 manually."
    exit 1
  fi
}

install_python3() {
  echo "Checking if Python3 is installed..."
  if is_installed python3; then
    echo "Python3 is already installed."
    # non-interactive: don't ask to update, just accept current
    current_version=$(get_installed_python_version)
    echo "Current Python3 version: $current_version"
  else
    echo "Python3 is not installed. Installing..."
    if [ -x "$(command -v apt-get)" ]; then
      sudo apt-get update && sudo apt-get install python3 python3-venv -y
    elif [ -x "$(command -v dnf)" ]; then
      sudo dnf install python3 python3-venv -y || sudo dnf install python3 -y
    elif [ -x "$(command -v pacman)" ]; then
      sudo pacman -S --noconfirm python
    elif [ -x "$(command -v zypper)" ]; then
      sudo zypper install -y python3 python3-venv
    else
      echo "Unsupported package manager. Please install Python3 manually."
      exit 1
    fi
  fi
}

install_git() {
  echo "Checking if Git is installed..."
  if is_installed git; then
    echo "Git is already installed."
  else
    echo "Git is not installed. Installing..."
    if [ -x "$(command -v apt-get)" ]; then
      sudo apt-get update && sudo apt-get install git -y
    elif [ -x "$(command -v dnf)" ]; then
      sudo dnf install git -y
    elif [ -x "$(command -v pacman)" ]; then
      sudo pacman -S --noconfirm git
    elif [ -x "$(command -v zypper)" ]; then
      sudo zypper install -y git
    else
      echo "Unsupported package manager. Please install Git manually."
      exit 1
    fi
  fi
}

install_build_tools() {
  echo "Installing system build dependencies for Geant4..."

  if [ -x "$(command -v apt-get)" ]; then
    sudo apt-get update
    sudo apt-get install -y \
      build-essential cmake ninja-build wget curl \
      qtbase5-dev libxerces-c-dev libssl-dev libexpat1-dev
  elif [ -x "$(command -v dnf)" ]; then
    sudo dnf install -y \
      gcc gcc-c++ make cmake ninja-build git wget curl \
      qt5-qtbase-devel xerces-c-devel openssl-devel expat-devel
  elif [ -x "$(command -v pacman)" ]; then
    sudo pacman -Syu --noconfirm
    sudo pacman -S --noconfirm \
      base-devel cmake ninja git wget curl \
      qt5-base xerces-c openssl expat
  elif [ -x "$(command -v zypper)" ]; then
    sudo zypper install -y \
      gcc gcc-c++ make cmake ninja git wget curl \
      libqt5-qtbase-devel libxerces-c-devel libopenssl-devel libexpat-devel
  else
    echo "Unsupported distro: no known package manager found."
    exit 1
  fi
}

setup_python_env() {
  echo "Setting up a Python virtual environment for Geant4 installation."

  # ensure venv module exists (only really needed on Debian/Ubuntu)
  if ! python3 -m venv --help &>/dev/null; then
    echo "venv module not found. Installing..."
    if [ -x "$(command -v apt-get)" ]; then
      sudo apt-get update && sudo apt-get install python3-venv -y
    elif [ -x "$(command -v dnf)" ]; then
      sudo dnf install python3-venv -y || true
    elif [ -x "$(command -v pacman)" ]; then
      sudo pacman -S --noconfirm python-virtualenv
    elif [ -x "$(command -v zypper)" ]; then
      sudo zypper install -y python3-venv
    fi
  fi

  python3 -m venv geant4_env
  # shellcheck source=/dev/null
  source geant4_env/bin/activate

  echo "Installing 'requests' and 'colorama' modules in the virtual environment..."
  pip install --upgrade pip
  pip install requests colorama

  echo "Python virtual environment configured and activated."
}

install_all_deps() {
  install_python3
  install_git
  install_build_tools
  setup_python_env
}
