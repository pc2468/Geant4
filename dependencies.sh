#!/usr/bin/env bash

set -e

detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    else
        echo "unknown"
    fi
}

install_deps_ubuntu() {
    sudo apt update
    sudo apt install -y \
        build-essential cmake git wget curl \
        qtbase5-dev libxerces-c-dev libssl-dev libexpat1-dev \
        python3 python3-pip ninja-build
}

install_deps_arch() {
    sudo pacman -Syu --noconfirm
    sudo pacman -S --noconfirm \
        base-devel cmake git wget curl \
        xerces-c qt5-base openssl expat ninja
}

install_deps_fedora() {
    sudo dnf install -y \
        gcc gcc-c++ make cmake git wget curl \
        qt5-qtbase-devel xerces-c-devel openssl-devel expat-devel ninja-build
}

distro=$(detect_distro)

case "$distro" in
    ubuntu|debian)
        install_deps_ubuntu
        ;;
    arch)
        install_deps_arch
        ;;
    fedora)
        install_deps_fedora
        ;;
    *)
        echo "Unsupported distro: $distro"
        exit 1
        ;;
esac
