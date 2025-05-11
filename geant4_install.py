import os
import sys
import shutil
import subprocess
import platform
import tempfile
import re
import requests
from urllib.parse import urljoin

def ensure_xdg_open_installed():
    if shutil.which("xdg-open") is None:
        print("xdg-open not found. Installing xdg-utils...")
        try:
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", "-y", "xdg-utils"], check=True)
            if shutil.which("xdg-open") is None:
                print("xdg-open still not found after install. Exiting.")
                sys.exit(1)
            else:
                print("xdg-utils installed successfully.")
        except subprocess.CalledProcessError as e:
            print("Failed to install xdg-utils. Error:", e)
            sys.exit(1)


def ensure_basic_utilities():
    """Ensure colorama and lsb-release are installed."""
    try:
        from colorama import Fore, Style, init
    except ImportError:
        print("[INFO] colorama not found. Attempting to install required packages...")

        package_managers = {
            "apt": "sudo apt update && sudo apt install -y python3-colorama lsb-release",
            "dnf": "sudo dnf install -y python3-colorama redhat-lsb-core",
            "yum": "sudo yum install -y python3-colorama redhat-lsb-core",
            "pacman": "sudo pacman -Sy --noconfirm python-colorama lsb-release",
            "zypper": "sudo zypper install -y python3-colorama lsb-release"
        }

        for manager, command in package_managers.items():
            if subprocess.call(f"command -v {manager}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                try:
                    subprocess.check_call(command, shell=True)
                    os.execv(sys.executable, [sys.executable] + sys.argv)
                except subprocess.CalledProcessError:
                    continue

        print("\033[95m[ACTION REQUIRED]\033[0m Install colorama and lsb-release manually:")
        print("  sudo apt install python3-colorama lsb-release")
        print("  sudo dnf install python3-colorama redhat-lsb-core")
        print("  sudo yum install python3-colorama redhat-lsb-core")
        print("  sudo pacman -Sy python-colorama lsb-release")
        sys.exit(1)

    init(autoreset=True)

ensure_basic_utilities()

from colorama import Fore, Style
def print_message(tag, color, message):
    print(f"{color}[{tag}]{Style.RESET_ALL} {message}")

print_info = lambda msg: print_message("INFO", Fore.CYAN, msg)
print_success = lambda msg: print_message("SUCCESS", Fore.GREEN, msg)
print_warning = lambda msg: print_message("WARNING", Fore.YELLOW, msg)
print_error = lambda msg: print_message("ERROR", Fore.RED, msg)
print_action = lambda msg: print_message("ACTION REQUIRED", Fore.MAGENTA, msg)

def run_command(command, description="", interactive=False, silent=False):
    if not silent:
        print_info(f"{description}...")

    try:
        if interactive:
            subprocess.run(command, shell=True, check=True)
        else:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace"   # 🛠️ This ignores bad bytes
            )
            for line in process.stdout:
                if not silent:
                    print(line, end='')
            process.wait()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, command)

        if not silent:
            print_success(f"{description} completed!")
        return 0
    except subprocess.CalledProcessError as e:
        if not silent:
            print_error(f"{description} failed: {e}")
        return e.returncode
def is_wsl():
    return "microsoft" in platform.uname().release.lower()

def detect_os():
    os_type = platform.system()
    distro = ""

    if os_type == "Linux":
        try:
            result = subprocess.run(["lsb_release", "-d"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                output = result.stdout.strip()
                match = re.search(r'Description:\s*(.*)', output)
                if match:
                    distro = match.group(1)
            else:
                raise Exception("lsb_release not available")
        except Exception:
            try:
                if os.path.exists("/etc/os-release"):
                    with open("/etc/os-release", "r") as f:
                        data = f.read()
                        match = re.search(r'^PRETTY_NAME="?([^"\n]*)"?', data, re.MULTILINE)
                        if match:
                            distro = match.group(1)
            except Exception as e:
                print_warning(f"Failed to detect distro: {e}")
                distro = "unknown"
    elif os_type == "Windows":
        distro = "windows"
    else:
        distro = "unknown"

    print_info(f"Detected OS: {os_type}, Distro: {distro}")

    return os_type, distro

def get_script_directory():
    return os.path.dirname(os.path.abspath(__file__))

def get_cpu_cores():
    print_info("(If you don't know your CPU core count, open a new terminal and run: `nproc`, then enter the number here.)")
    while True:
        try:
            cores = int(input("Enter the number of CPU cores for compilation: ").strip())
            if cores > 0:
                return cores
        except ValueError:
            pass
        print_warning("Invalid input. Try again.")


def install_packages(distro):
    distro_lower = distro.lower()

    if "arch" in distro_lower:
        pkg_cmd = "sudo pacman -Sy --noconfirm ..."
    elif any(name in distro_lower for name in ["ubuntu", "debian", "mint"]):
        pkg_cmd = "sudo apt update && sudo apt install -y ..."
    elif "opensuse" in distro_lower:
        pkg_cmd = "sudo zypper install -y ..."
    elif any(name in distro_lower for name in ["rocky", "rhel"]):
        pkg_cmd = "sudo dnf install -y ..."
    elif "fedora" in distro_lower:
        if platform.release().startswith("41"):
            pkg_cmd = "sudo dnf5 install -y ..."
        else:
            pkg_cmd = "sudo dnf install -y ..."
    else:
        print_warning("Distro not recognized. Please install dependencies manually.")
        return
    run_command(pkg_cmd, "Installing required packages", interactive=True)

def check_dependencies():
    missing = []

    if run_command("which qmake", silent=True) != 0:
        missing.append("Qt5 (qmake)")

    if run_command("ldconfig -p | grep libGL", silent=True) != 0:
        missing.append("OpenGL (libGL)")

    if missing:
        print_error(f"Missing dependencies: {', '.join(missing)}")
        print_action("You can choose to install them manually later.")

        choice = prompt("Do you want to [C]ontinue or [A]bort? [c/a] ").strip().lower()
        if choice == "a":
            sys.exit("Aborted by user due to missing dependencies.")
        else:
            print_warning("Continuing despite missing dependencies.")
    else:
        print_success("All required dependencies are present.")
def prompt(message):
    if args.non_interactive or args.yes_to_all:
        return 'c'
    return input(message)


def detect_geant4_version(source_dir):
    import fnmatch

    match = re.search(r"geant4-v(\d+)\.(\d+)\.(\d+)", source_dir)
    if match:
        major, minor, patch = map(int, match.groups())
        return (major, minor, patch)

    version_file = None
    for root, dirs, files in os.walk(source_dir):
        for filename in fnmatch.filter(files, "G4Version.hh"):
            version_file = os.path.join(root, filename)
            break
        if version_file:
            break

    if version_file:
        try:
            with open(version_file, "r") as f:
                content = f.read()
                major = int(re.search(r"#define G4VERSION_MAJOR (\d+)", content).group(1))
                minor = int(re.search(r"#define G4VERSION_MINOR (\d+)", content).group(1))
                patch = int(re.search(r"#define G4VERSION_PATCH (\d+)", content).group(1))
                return (major, minor, patch)
        except Exception:
            return None
    else:
        return None


def get_latest_geant4_version():
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Referer": "https://geant4.web.cern.ch/"
    }
    
    try:
        response = requests.get("https://gitlab.cern.ch/geant4/geant4/-/tags", headers=headers)
        response.raise_for_status()
        
        matches = re.findall(r'v(\d+\.\d+(?:\.\d+)?)', response.text)
        versions = sorted(set(matches), key=lambda x: list(map(int, x.split("."))), reverse=True)
        
        if not versions:
            print_error("Could not detect Geant4 versions.")
            sys.exit(1)

        print_info("Available Geant4 versions:")
        for i, ver in enumerate(versions[:5]):
            print(f"  [{i+1}] v{ver}")

        while True:
            try:
                choice = int(input("Choose a version to install (1-5): ").strip())
                if 1 <= choice <= 5:
                    return versions[choice - 1]
            except ValueError:
                pass
            print_warning("Invalid input. Try again.")
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to retrieve Geant4 versions: {e}")
        sys.exit(1)


def install_packages(distro, geant_version):
    distro_lower = distro.lower()

    if "arch" in distro_lower:
        family = "arch"
        base_packages = [
            "cmake", "gcc", "binutils",
            "libx11", "libxpm", "libxft", "libxext", "glew",
            "libjpeg-turbo", "libpng", "libtiff", "giflib",
            "libxml2", "openssl", "fftw",
            "qt5-base", "qt5-tools", "mesa", "glu", "libxmu"
        ]
        install_cmd = "sudo pacman -Sy --noconfirm"
    elif any(name in distro_lower for name in ["ubuntu", "debian", "mint"]):
        family = "debian"
        base_packages = [
            "cmake-curses-gui", "cmake", "g++", "gcc", "binutils",
            "libx11-dev", "libxpm-dev", "libxft-dev", "libxext-dev",
            "libglew-dev", "libjpeg-dev", "libpng-dev", "libtiff-dev", "libgif-dev",
            "libxml2-dev", "libssl-dev", "libfftw3-dev",
            "qtbase5-dev", "qtchooser", "qttools5-dev-tools", "qt3d5-dev",
            "libgl1-mesa-dev", "libglu1-mesa-dev", "libxmu-dev"
        ]
        install_cmd = "sudo apt update && sudo apt install -y"
    elif "opensuse" in distro_lower:
        family = "opensuse"
        base_packages = [
            "cmake", "cmake-curses-gui", "cmake-gui", "gcc", "gcc-c++",
            "libX11-devel", "libXpm-devel", "libXft-devel", "libXext-devel",
            "glew-devel", "libjpeg-devel", "libpng-devel", "libtiff-devel", "giflib-devel",
            "libxml2-devel", "libopenssl-devel", "fftw3-devel",
            "libqt5-qtbase-devel", "libqt5-qttools-devel", "libqt5-qt3d-devel",
            "Mesa-libGL-devel", "Mesa-libGLU-devel", "libXmu-devel"
        ]
        install_cmd = "sudo zypper install -y"
    elif any(name in distro_lower for name in ["rocky", "rhel"]):
        family = "rhel"
        base_packages = [
            "cmake", "cmake-curses-gui", "cmake-gui", "gcc", "gcc-c++", "binutils",
            "libX11-devel", "libXpm-devel", "libXft-devel", "libXext-devel",
            "glew-devel", "libjpeg-turbo-devel", "libpng-devel", "libtiff-devel", "giflib-devel",
            "libxml2-devel", "openssl-devel", "fftw-devel",
            "qt5-qtbase-devel", "qt5-qttools-devel", "qt5-qt3d-devel",
            "mesa-libGL-devel", "mesa-libGLU-devel", "libXmu-devel"
        ]
        install_cmd = "sudo dnf install -y"
    elif "fedora" in distro_lower:
        family = "fedora"
        base_packages = [
            "cmake", "cmake-curses-gui", "cmake-gui", "gcc", "gcc-c++", "binutils",
            "qt5-qtbase-devel", "qt5-qttools-devel", "qt5-qt3d-devel",
            "glew-devel", "libjpeg-turbo-devel", "libpng-devel", "libtiff-devel", "giflib-devel",
            "libxml2-devel", "openssl-devel", "fftw-devel",
            "mesa-libGL-devel", "mesa-libGLU-devel", "libXmu-devel"
        ]
        install_cmd = "sudo dnf5 install -y" if platform.release().startswith("41") else "sudo dnf install -y"
    else:
        print_warning("Distro not recognized. Please install dependencies manually.")
        return

    version_pkg_addons = {
        "11.2": {
            "debian": ["libtbb-dev"],
            "arch": ["tbb"],
            "fedora": ["tbb-devel"],
            "rhel": ["tbb-devel"],
            "opensuse": ["tbb-devel"]
        },
    }

    extra_packages = version_pkg_addons.get(geant_version, {}).get(family, [])
    all_packages = base_packages + extra_packages

    pkg_cmd = f"{install_cmd} {' '.join(all_packages)}"

    run_command(pkg_cmd, "Installing dependencies", interactive=True)




def verify_geant4_install(install_path):
    geant4_config = os.path.join(install_path, "bin", "geant4-config")
    if os.path.exists(geant4_config):
        result = subprocess.run([geant4_config, "--version"], capture_output=True, text=True)
        print_success(f"Geant4 Version Installed: {result.stdout.strip()}")
    else:
        print_warning("geant4-config not found. Installation may not be correct.")

def add_versioned_alias(version, install_path):
    alias_name = f"geant4-{version.replace('.', '_')}"
    alias_command = f'alias {alias_name}="source {install_path}/bin/geant4.sh"'
    bashrc_path = os.path.expanduser("~/.bashrc")

    with open(bashrc_path, "a") as bashrc_file:
        bashrc_file.write(f"\n{alias_command}\n")

    print_success(f"Alias '{alias_name}' added to ~/.bashrc")



def install_geant4():
    os_type, distro = detect_os()
    if os_type == "Windows":
        print_warning("Script only supports Linux or WSL. Windows script is under development.")
        sys.exit(1)

    script_dir = get_script_directory()
    geant4_dir = os.path.join(script_dir, "Geant4")
    os.makedirs(geant4_dir, exist_ok=True)
    os.chdir(geant4_dir)

    version = get_latest_geant4_version()
    tarball = f"geant4-v{version}.tar.gz"
    tar_url = f"https://gitlab.cern.ch/geant4/geant4/-/archive/v{version}/{tarball}"
    src_dir = f"geant4-v{version}"
    build_dir = f"geant4-v{version}-build"

    if os.path.exists(tarball):
        print_warning(f"{tarball} already exists.")
        choice = input("Do you want to [R]edownload, [S]kip, or [A]bort? (R/S/A): ").strip().lower()
        if choice == 'r':
            run_command(f"rm -f {tarball}", "Removing existing tarball")
            run_command(f"wget {tar_url}", "Downloading Geant4 source")
        elif choice == 's':
            print_info("Skipping download and extraction.")
        else:
            print_info("Aborting.")
            sys.exit(0)
    else:
        run_command(f"wget {tar_url}", "Downloading Geant4 source")

    if not (os.path.exists(src_dir) and os.listdir(src_dir)):
        run_command(f"tar -xvzf {tarball}", "Extracting Geant4 source")

    if os.path.exists(build_dir) and os.listdir(build_dir):
        print_warning(f"Build directory '{build_dir}' is not empty.")
        choice = input("[C]lear, [S]kip, or [A]bort? (C/S/A): ").strip().lower()
        if choice == 'c':
            run_command(f"rm -rf {build_dir}", "Clearing build directory")
            os.makedirs(build_dir)
        elif choice == 's':
            print_info("Continuing with existing build directory.")
        else:
            print_info("Aborting.")
            sys.exit(0)
    else:
        os.makedirs(build_dir)

    os.chdir(build_dir)
    install_packages(distro, version)  # Pass the Geant4 version here

    install_path = os.path.join(script_dir, "Geant4", f"geant4-v{version}-install")
    print_info(f"Install path: {install_path}")


    instructions = f"""
[INSTRUCTIONS]
1. After CMake opens, you'll see: EMPTY CACHE
   - Press 'c' to configure
   - Press 'e' to exit the warning

2. Now edit the following settings (use arrow keys to navigate):
   - First, go to CMAKE_INSTALL_PREFIX, press Enter,
     then paste the following path using Shift+Ctrl+V:
       {install_path}
     Press Enter again. If it updates from /usr/local, it's set.

Turn ON (ideal settings):
   - GEANT4_INSTALL_DATA
   - GEANT4_USE_OPENGL_X11
   - GEANT4_USE_QT
   - GEANT4_USE_RAYTRACER_X11
   (You can enable more features if desired.)

4. Press 'c' again to configure. Repeat until 'g' is available.
5. Press 'g' to generate the Makefile.
6. After closing CMake, return to the terminal to continue the installation.
    """

    with open('geant4_install_instructions.txt', 'w') as f:
        f.write(instructions.strip())
    ensure_xdg_open_installed() 

    try:
        if is_wsl():
            subprocess.run(["powershell.exe", "Start-Process", "geant4_install_instructions.txt"], check=True)
            print_info("Opened instructions using Windows default app via WSL.")
        else:
            subprocess.run(["xdg-open", "geant4_install_instructions.txt"], check=True)
            print_info("Opened instructions using xdg-open.")
    except subprocess.CalledProcessError:
        print_warning("GUI open failed. Falling back to terminal display.")
        run_command("less geant4_install_instructions.txt", "Displaying instructions in terminal", interactive=True)


    input("Press Enter to open CMake configuration...")

    run_command(f"ccmake ../{src_dir}", "Running CMake", interactive=True)


    input("Press Enter after completing CMake configuration to continue...")
    cores = get_cpu_cores()
    run_command(f"make -j{cores}", "Compiling Geant4")
    run_command("sudo make install", "Installing Geant4")

    print_success("Geant4 installed successfully.")

    verify_geant4_install(install_path)
    add_versioned_alias(version, install_path)

    major_version = int(version.split(".")[0])
    if major_version < 11:
        bashrc_path = os.path.expanduser("~/.bashrc")
        setup_command = f"source {install_path}/bin/geant4.sh"
        with open(bashrc_path, "a") as bashrc:
            bashrc.write(f"\n{setup_command}\n")
        print_info("Geant4 environment setup added to ~/.bashrc")
        print_info("Run 'source ~/.bashrc' or restart terminal to apply changes.")

    choice = input("Do you want to build and run Example B1 to verify installation? (y/n): ").strip().lower()
    if choice == 'y':
        b1_example_path = os.path.join(install_path, "share", "Geant4", "examples", "basic", "B1")
        build_path = os.path.join(b1_example_path, "build")
        geant4_cmake_dir = os.path.join(install_path, "lib", "Geant4-11.3.2")

        try:
            os.makedirs(build_path, exist_ok=True)
            os.chdir(build_path)

            if not os.path.exists(geant4_cmake_dir):
                raise FileNotFoundError(f"Geant4 CMake directory not found: {geant4_cmake_dir}")

            cmake_command = f"cmake -DGeant4_DIR={geant4_cmake_dir} .."
            run_command(cmake_command, "Configuring Example B1")
            run_command(f"make -j{cores}", "Building Example B1")

            print_info("Running Example B1...")
            subprocess.run(["./exampleB1"], check=True)
            print_success("Example B1 ran successfully. Geant4 is working.")
        except Exception as e:
            print_error(f"Failed during Example B1 verification: {e}")
    else:
        print_success("Installation completed. You can manually test Geant4 later.")




if __name__ == "__main__":
    install_geant4()
