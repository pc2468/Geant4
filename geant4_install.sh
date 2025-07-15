#!/bin/bash

is_installed() {
  dpkg-query -l "$1" &>/dev/null || rpm -q "$1" &>/dev/null || pacman -Qs "$1" &>/dev/null
}

get_installed_python_version() {
  python3 --version 2>&1 | awk '{print $2}'
}

update_python3() {
  echo "Updating Python3..."
  if [ -x "$(command -v apt-get)" ]; then
    sudo apt-get update && sudo apt-get install --only-upgrade python3
  elif [ -x "$(command -v dnf)" ]; then
    sudo dnf upgrade python3
  elif [ -x "$(command -v pacman)" ]; then
    sudo pacman -Syu python
  elif [ -x "$(command -v zypper)" ]; then
    sudo zypper update python3
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

    # Find latest version
    if [ -x "$(command -v apt-get)" ]; then
      latest_version=$(apt-cache policy python3 | grep 'Candidate' | awk '{print $2}')
    elif [ -x "$(command -v dnf)" ]; then
      latest_version=$(dnf info python3 | grep 'Version' | awk '{print $3}')
    elif [ -x "$(command -v pacman)" ]; then
      latest_version=$(pacman -Qi python | grep 'Version' | awk '{print $3}')
    elif [ -x "$(command -v zypper)" ]; then
      latest_version=$(zypper info python3 | grep 'Version' | awk '{print $3}')
    else
      echo "Unsupported package manager. Skipping version check."
      return
    fi

    echo "Latest Python3 version available: $latest_version"

    if [ "$current_version" != "$latest_version" ]; then
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
      sudo apt-get update && sudo apt-get install python3
    elif [ -x "$(command -v dnf)" ]; then
      sudo dnf install python3
    elif [ -x "$(command -v pacman)" ]; then
      sudo pacman -S python
    elif [ -x "$(command -v zypper)" ]; then
      sudo zypper install python3
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
      sudo apt-get update && sudo apt-get install git
    elif [ -x "$(command -v dnf)" ]; then
      sudo dnf install git
    elif [ -x "$(command -v pacman)" ]; then
      sudo pacman -S git
    elif [ -x "$(command -v zypper)" ]; then
      sudo zypper install git
    else
      echo "Unsupported package manager. Please install Git manually."
      exit 1
    fi
  fi
}

install_python3
install_git

echo "Downloading required Geant4 files..."
curl -fsSL https://github.com/pc2468/Geant4/raw/main/install_geant4.sh -o install_geant4.sh
curl -fsSL https://github.com/pc2468/Geant4/raw/main/geant4_install.py -o geant4_install.py

chmod +x install_geant4.sh

echo "Running Geant4 installation script..."
python3 geant4_install.py
