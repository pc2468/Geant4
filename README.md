# Geant4 Installer for Linux — One Script to Build Them All

Ever tried installing Geant4 on Linux and ended up in dependency hell, drowning in CMake flags and missing libraries?

Yeah, me too. So I wrote a script.

This project gives you a simple way to build and install Geant4 on any major Linux system — even WSL on Windows. No manual downloading, no guesswork. Just copy a few commands into your terminal and let it handle the rest.

---
## Two Ways to Install Geant4
**1. Easy Automated Way (Recommended)**  
The easiest way to install Geant4 is by running a single command. This method will automatically take care of all dependencies, download the installation script, and set everything up for you.  
Just run the following command in your terminal:
```bash
bash -c "$(curl -fsSL https://github.com/pc2468/Geant4/raw/main/geant4_install.sh)"
```
What Happens When You Run the Command:
- This command will handle everything! It checks if you have Python3 and Git installed. If not, it installs them automatically.
- It clones the Geant4 repo from GitHub: It downloads all the files needed for the installation, including the `geant4_install.py` script.
- The script is then executed: It will guide you through the installation process, from downloading the Geant4 source to building and setting it up on your system.

No more fiddling around with dependencies and CMake flags. This method is like a one-click installer!

**2. Manual Installation (Optional)**
If you prefer to install Geant4 manually or want more control over the process, you can follow the instructions in the [Geant4 Manual Installation Guide](https://github.com/pc2468/Geant4/raw/main/geant4_manual_install.pdf).  
This guide will walk you through the entire process step-by-step, including manually cloning the repository, installing dependencies, and building Geant4 from source.

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

**1. Run the One-Line Command**  
Instead of cloning the repo manually, just run this one-line command in your terminal:
```bash
bash -c "$(curl -fsSL https://github.com/pc2468/Geant4/raw/main/geant4_install.sh)"
```
What’s Happening Here?
- `curl -fsSL`: This fetches the script from GitHub. It’s like getting a file from the internet.
-  `bash -c`: This runs the file (or script) we just downloaded.
The script will handle everything for you — from checking if Python3 is installed, to ensuring Git is present, and then setting up Geant4.

**2. Answer a Few Questions**  
Once the script runs, you'll be prompted with a few simple questions to help guide the installation. Just follow the on-screen instructions, and you'll be good to go!

**3. Wait for the Magic**  
The script will take care of:
- Installing required software packages
- Downloading the Geant4 source
- Configuring and building Geant4 using CMake
- Installing Geant4 and setting up the environment for you  

It will even set up a shortcut so you can use Geant4 immediately after installation. You’ll see messages on your screen letting you know what’s happening — it’s like watching a cooking show, except the computer does the hard work.

## What It Looks Like

Here’s a sneak peek of what you’ll see as the script runs:

| Step | Screenshot |
|------|------------|
| Script starts running | ![Step 1](Screenshot/step1.png) |
| Downloads the Geant4 source | ![Step 2](Screenshot/step2.png) |
| Opens a short text guide to walk you through CMake config | ![Step 3](Screenshot/step3.png) |
| Compiling and installing (this takes a while) | ![Step 4](Screenshot/step4.png) |
| Done! Geant4 is installed and ready to use | ![Step 5](Screenshot/step5.png) |
| Run B1 example to verify installation | ![B1 Example Screenshot](Screenshot/b1_example.png) |

##Troubleshooting
If you run into any issues during installation, here are a few things to check:
- Missing dependencies: The script tries to install all necessary dependencies. If you see a missing package error, check your internet connection or manually install missing packages using your system’s package manager.
- Permission issues: If you encounter permission errors, try running the script with `sudo` for elevated privileges:
```bash
sudo bash -c "$(curl -fsSL https://github.com/pc2468/Geant4/raw/main/geant4_install.sh)"
```
- CMake errors: If something goes wrong during the CMake configuration, make sure you’ve followed the prompts carefully and ensured all dependencies were installed.

---

## Questions or Issues?

If you have any questions, issues, or suggestions, feel free to:

- **Open an issue** on the [GitHub repository](https://github.com/pc2468/Geant4/issues)
- **Leave a comment** on any relevant GitHub page
- **Email me directly** at [changdeprathamesh@gmail.com](mailto:changdeprathamesh@gmail.com)

I’ll do my best to get back to you as quickly as possible.

---

Happy coding and enjoy your Geant4 experience!

---

## 📜 License

This project is licensed under the MIT License.

```text
MIT License

Copyright (c) 2025 Prathamesh Changde

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

