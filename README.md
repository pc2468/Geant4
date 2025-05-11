# Geant4 Installer for Linux — One Script to Build Them All

Ever tried installing Geant4 on Linux and ended up in dependency hell, drowning in CMake flags and missing libraries?

Yeah, me too. So I wrote a script.

This project gives you a simple way to build and install Geant4 on any major Linux system — even WSL on Windows. No manual downloading, no guesswork. Just copy a few commands into your terminal and let it handle the rest.

---
##Prerequisites
Before you run the script, ensure you have the following:  

**Python 3: Check if you have Python 3 installed by running**
```bash
python3 --version
```
If you don't have Python 3 installed, you can install it by following the [official Python installation guide.](https://www.python.org/downloads/)  

**Git: To clone the repository, you'll need Git. Check if it's installed**
```bash
git --version
```
If not, you can install Git by running:
```bash
sudo apt install git  # For Ubuntu/Debian-based systems
sudo yum install git  # For Fedora/RHEL-based systems
sudo pacman -Sy git   # For Arch-based systems (I use arch btw)
```

## What You'll Do — and What Happens

### You Will:
- Run a Python script: `geant4_install.py`
- Answer a few friendly questions
- Read a tiny popup with setup instructions (don’t worry, it’s simple)
- Let your computer build Geant4 while you grab snacks

### The Script Will:
- Detect your Linux version (Ubuntu, Fedora, Arch, etc.)
- Install everything Geant4 needs
- Download the official Geant4 source
- Guide you through a CMake configuration (just press ‘c’ and then ‘g’)
- Build and install Geant4
- Set up a shortcut so you can use it immediately

---

## Quick Start — Step-by-Step

You don’t need to download anything manually. Just open a terminal and follow these steps:

**1. Clone this repository from GitHub**  
This pulls down everything — the script, guide, and screenshots — into a folder named `Geant4`.

```bash
git clone https://github.com/pc2468/Geant4
```

**2. Move into that folder**

```bash
cd Geant4
```

**3.Check if the installer script is there**
```bash
ls
```
You should see a file named geant4_install.py. This is the script you'll run.

**4. Run the installer**
```bash
python3 geant4_install.py
```
This will launch the automated setup. Just follow the prompts.
That’s it. The script will take care of the rest.


## What It Looks Like

Here’s what you’ll see as the script runs:

| Step | Screenshot |
|------|------------|
| Script starts running | ![Step 1](screenshots/step1.png) |
| It checks your Linux version and installs required packages | ![Step 2](screenshots/step2.png) |
| Downloads the Geant4 source | ![Step 3](screenshots/step3.png) |
| Opens a short text guide to walk you through CMake config | ![Step 4](screenshots/step4.png) |
| Compiling and installing (this takes a while) | ![Step 5](screenshots/step5.png) |
| Done! Geant4 is installed and ready to use | ![Step 6](screenshots/step6.png) |
| Run B1 example to verify installation | ![B1 Example Screenshot](screenshots/b1_example.png) |

##Troubleshooting
If you run into any issues during installation, here are a few things to check:
- Missing dependencies: The script tries to install all necessary dependencies. If you see a missing package error, check your internet connection or manually install missing packages using your system’s package manager.
- Permission issues: If you encounter permission errors, try running the script with `sudo` for elevated privileges:
```bash
sudo python3 geant4_install.py
```
- CMake errors: If something goes wrong during the CMake configuration, make sure you’ve followed the prompts carefully and ensured all dependencies were installed.

---

## Questions or Issues?

If you have any questions, issues, or suggestions, feel free to:

- **Open an issue** on the [GitHub repository](https://github.com/pc2468/Geant4/issues)
- **Leave a comment** on any relevant GitHub page
- **Email me directly** at [your_email@example.com](mailto:changdeprathamesh@gmail.com)

I’ll do my best to get back to you as quickly as possible.

---

Happy coding and enjoy your Geant4 experience!
