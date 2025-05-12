#!/bin/bash

is_installed() {
  dpkg-query -l "$1" &>/dev/null || rpm -q "$1" &>/dev/null || pacman -Qs "$1" &>/dev/null
}

install_python3() {
  echo "Installing Python3..."
  if is_installed python3; then
    echo "Python3 is already installed."
  else
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
  echo "Installing Git..."
  if is_installed git; then
    echo "Git is already installed."
  else
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

echo "Cloning the Geant4 repository..."
git clone https://github.com/pc2468/Geant4.git

cd Geant4 || exit

chmod +x install_geant4.sh

echo "Running Geant4 installation script..."
python3 geant4_install.py
