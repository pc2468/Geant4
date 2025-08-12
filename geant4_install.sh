#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

is_installed() {
  dpkg-query -l "$1" &>/dev/null || rpm -q "$1" &>/dev/null || pacman -Qs "$1" &>/dev/null || zypper se -i "$1" &>/dev/null
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
    current_version=$(get_installed_python_version)
    echo "Current Python3 version: $current_version"

    if [ -x "$(command -v apt-get)" ]; then
      latest_version=$(apt-cache policy python3 | grep 'Candidate' | awk '{print $2}')
    elif [ -x "$(command -v dnf)" ]; then
      latest_version=$(dnf info python3 | grep 'Version' | awk '{print $3}')
    elif [ -x "$(command -v pacman)" ]; then
      latest_version=$(pacman -Si python | awk '/Version/ {print $3}' | cut -d'-' -f1)
    elif [ -x "$(command -v zypper)" ]; then
      latest_version=$(zypper info python3 | grep 'Version' | awk '{print $3}')
    else
      echo "Unsupported package manager. Skipping version check."
      return
    fi

    echo "Latest Python3 version available: $latest_version"

    if [ -n "$latest_version" ] && [ "$current_version" != "$latest_version" ]; then
      echo "A newer Python3 version is available."
      read -p "Would you like to update Python3 now? (y/n): " choice
      if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
        update_python3
      else
        echo "Skipping Python3 update."
      fi
    else
      echo "Python3 is already up to date."
    fi

  else
    echo "Python3 is not installed. Installing..."
    if [ -x "$(command -v apt-get)" ]; then
      sudo apt-get update && sudo apt-get install python3 -y
    elif [ -x "$(command -v dnf)" ]; then
      sudo dnf install python3 -y
    elif [ -x "$(command -v pacman)" ]; then
      sudo pacman -S python --noconfirm
    elif [ -x "$(command -v zypper)" ]; then
      sudo zypper install python3 -y
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
      sudo pacman -S git --noconfirm
    elif [ -x "$(command -v zypper)" ]; then
      sudo zypper install git -y
    else
      echo "Unsupported package manager. Please install Git manually."
      exit 1
    fi
  fi
}

setup_python_env() {
  echo "Setting up a Python virtual environment for Geant4 installation."
  if ! python3 -m venv --help &>/dev/null; then
    echo "venv module not found. Installing python3-venv..."
    if [ -x "$(command -v apt-get)" ]; then
      sudo apt-get update && sudo apt-get install python3-venv -y
    elif [ -x "$(command -v dnf)" ]; then
      sudo dnf install python3-venv -y
    elif [ -x "$(command -v pacman)" ]; then
      sudo pacman -S python-virtualenv --noconfirm
    elif [ -x "$(command -v zypper)" ]; then
      sudo zypper install python3-venv -y
    fi
  fi

  python3 -m venv geant4_env
  source geant4_env/bin/activate

  echo "Installing 'requests' and 'colorama' modules in the virtual environment..."
  pip install --upgrade pip
  pip install requests colorama

  echo "Python virtual environment configured and activated."
}

install_python3
install_git
setup_python_env

# Download geant4_install.py if missing
if [ ! -f geant4_install.py ]; then
  echo "Downloading geant4_install.py..."
  curl -fsSL -o geant4_install.py https://raw.githubusercontent.com/pc2468/Geant4/main/geant4_install.py || {
    echo "Failed to download geant4_install.py. Please check the URL."
    deactivate
    exit 1
  }
fi

echo "Running Geant4 installation script..."
./geant4_env/bin/python geant4_install.py

deactivate
