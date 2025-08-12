# If you're reading this, congratulations! You've just stumbled upon my first working script—yes, it's messy, yes, it's imperfect, 
# but hey, I'm learning. If you spot something that looks broken, it's probably intentional (just kidding, I’m still figuring things out). 
# But remember, if it ain't broke, don't fix it... unless it’s really broken, then feel free to fix it... eventually.
# And hey, if you have any suggestions, I'm all ears—I'm always ready to improve, just as soon as I figure out how this all works!
# Thanks for checking it out. I hope it does *something* useful for you.

import os
import sys
import shutil
import subprocess
import platform
import tempfile
import re
import requests
from urllib.parse import urljoin
import io

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    print("WARNING: colorama not found. Please install with 'pip install colorama' for colored output.")
    class DummyColorama:
        def __getattr__(self, name):
            return ""
    Fore = Style = DummyColorama()

def print_message(tag, color, message):
    print(f"{color}[{tag}]{Style.RESET_ALL} {message}")

print_info = lambda msg: print_message("INFO", Fore.CYAN, msg)
print_success = lambda msg: print_message("SUCCESS", Fore.GREEN, msg)
print_warning = lambda msg: print_message("WARNING", Fore.YELLOW, msg)
print_error = lambda msg: print_message("ERROR", Fore.RED, msg)
print_action = lambda msg: print_message("ACTION REQUIRED", Fore.MAGENTA, msg)

def run_command(command, description="", interactive=False, silent=False):
    if not silent:
        print_info(f"Running command: {command} ({description})")

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
                errors="replace"
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
        print_error(f"Command output: {e.output}")
        return e.returncode

def is_wsl():
    return "microsoft" in platform.uname().release.lower()

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

def prompt(message):
    try:
        if os.isatty(sys.stdin.fileno()):
            return input(message)
        else:
            return 'y'
    except (io.UnsupportedOperation, AttributeError):
        return 'y'
    
def detect_os():
    os_type = platform.system()
    full_info = ""

    if os_type == "Linux":
        try:
            if shutil.which("fastfetch"):
                result = subprocess.run(
                    ["fastfetch", "--raw"], capture_output=True, text=True, check=True
                )
                full_info = result.stdout.strip()
            elif shutil.which("neofetch"):
                result = subprocess.run(
                    ["neofetch", "--off"], capture_output=True, text=True, check=True
                )
                full_info = result.stdout.strip()
            else:
                try:
                    result = subprocess.run(
                        ["lsb_release", "-a"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        check=False
                    )
                    if result.returncode == 0:
                        full_info = result.stdout.strip()
                    else:
                        raise FileNotFoundError
                except (FileNotFoundError, OSError):
                    if os.path.exists("/etc/os-release"):
                        with open("/etc/os-release", "r") as f:
                            full_info = f.read().strip()
                    else:
                        full_info = "Linux (unknown distribution)"
        except Exception as e:
            print_warning(f"Failed to detect Linux distribution details: {e}")
            full_info = "Linux (detection failed)"
    elif os_type == "Windows":
        full_info = "Windows OS: " + platform.platform()
    else:
        full_info = f"Unsupported OS: {os_type}"

    print_info(f"Detected OS info:\n{full_info}")
    return os_type, full_info


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
    headers = {"User-Agent": "Mozilla/5.0"}

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
                    selected = versions[choice - 1]

                    tarball_url = f"https://gitlab.cern.ch/geant4/geant4/-/archive/v{selected}/geant4-v{selected}.tar.gz"

                    print_info(f"Checking if tarball exists: {tarball_url}")
                    test_response = requests.head(tarball_url)

                    if test_response.status_code != 200:
                        print_warning(f"Could not find source tarball for v{selected}.")
                        print_warning("This probably means it's not released yet.")
                        print_action("Check your version or pick an older stable version.")
                        try_again = input("Do you want to choose a different version? [Y/n]: ").strip().lower()
                        if try_again != "n":
                            continue
                        else:
                            sys.exit("Aborted by user.")

                    return selected

            except ValueError:
                pass
            print_warning("Invalid input. Try again.")
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to retrieve Geant4 versions: {e}")
        sys.exit(1)

def install_packages(distro, geant_version):
    distro_lower = distro.lower()
    
    package_map = {
        "arch": {
            "base": ["cmake", "gcc", "binutils", "libx11", "libxpm", "libxft", "libxext", "glew", "libjpeg-turbo", "libpng", "libtiff", "giflib", "libxml2", "openssl", "fftw", "qt5-base", "qt5-tools", "mesa", "glu", "libxmu"],
            "addons": {
                "11": ["tbb"]
            },
            "install_cmd": "sudo pacman -Sy --noconfirm"
        },
        "debian": {
            "base": ["cmake-curses-gui", "cmake", "g++", "gcc", "binutils", "libx11-dev", "libxpm-dev", "libxft-dev", "libxext-dev", "libglew-dev", "libjpeg-dev", "libpng-dev", "libtiff-dev", "libgif-dev", "libxml2-dev", "libssl-dev", "libfftw3-dev", "qtbase5-dev", "qtchooser", "qttools5-dev-tools", "qt3d5-dev", "libgl1-mesa-dev", "libglu1-mesa-dev", "libxmu-dev"],
            "addons": {
                "11": ["libtbb-dev"]
            },
            "install_cmd": "sudo apt update && sudo apt install -y"
        },
        "opensuse": {
            "base": ["cmake", "cmake-curses-gui", "cmake-gui", "gcc", "gcc-c++", "libX11-devel", "libXpm-devel", "libXft-devel", "libXext-devel", "glew-devel", "libjpeg-devel", "libpng-devel", "libtiff-devel", "giflib-devel", "libxml2-devel", "libopenssl-devel", "fftw3-devel", "libqt5-qtbase-devel", "libqt5-qttools-devel", "libqt5-qt3d-devel", "Mesa-libGL-devel", "Mesa-libGLU-devel", "libXmu-devel"],
            "addons": {
                "11": ["tbb-devel"]
            },
            "install_cmd": "sudo zypper install -y"
        },
        "rhel": {
            "base": ["cmake", "cmake-curses-gui", "cmake-gui", "gcc", "gcc-c++", "binutils", "libX11-devel", "libXpm-devel", "libXft-devel", "libXext-devel", "glew-devel", "libjpeg-turbo-devel", "libpng-devel", "libtiff-devel", "giflib-devel", "libxml2-devel", "openssl-devel", "fftw-devel", "qt5-qtbase-devel", "qt5-qttools-devel", "qt5-qt3d-devel", "mesa-libGL-devel", "mesa-libGLU-devel", "libXmu-devel"],
            "addons": {
                "11": ["tbb-devel"]
            },
            "install_cmd": "sudo dnf install -y"
        },
        "fedora": {
            "base": ["cmake", "cmake-curses-gui", "cmake-gui", "gcc", "gcc-c++", "binutils", "qt5-qtbase-devel", "qt5-qttools-devel", "qt5-qt3d-devel", "glew-devel", "libjpeg-turbo-devel", "libpng-devel", "libtiff-devel", "giflib-devel", "libxml2-devel", "openssl-devel", "fftw-devel", "mesa-libGL-devel", "mesa-libGLU-devel", "libXmu-devel"],
            "addons": {
                "11": ["tbb-devel"]
            },
            "install_cmd": "sudo dnf install -y" 
        }
    }

    if "arch" in distro_lower:
        family = "arch"
    elif any(name in distro_lower for name in ["ubuntu", "debian", "mint"]):
        family = "debian"
    elif "opensuse" in distro_lower:
        family = "opensuse"
    elif any(name in distro_lower for name in ["rocky", "rhel"]):
        family = "rhel"
    elif "fedora" in distro_lower:
        family = "fedora"
    else:
        print_warning("Distro not recognized. Please install dependencies manually.")
        return

    major_version = geant_version.split('.')[0]
    distro_config = package_map.get(family, {})
    base_packages = distro_config.get("base", [])
    extra_packages = distro_config.get("addons", {}).get(major_version, [])
    install_cmd = distro_config.get("install_cmd")

    all_packages = base_packages + extra_packages

    if not all_packages:
        print_warning(f"No specific packages found for {distro} and Geant4 v{major_version}. Please install manually.")
        return
    
    print_action("The following packages will be installed to meet Geant4's dependencies:")
    print(" ".join(all_packages))
    
    choice = prompt("Do you want to proceed with the automatic installation? [y/n] ")
    if choice.lower() == 'y':
        pkg_cmd = f"{install_cmd} {' '.join(all_packages)}"
        run_command(pkg_cmd, "Installing required packages", interactive=True)
    else:
        print_warning("Skipping automatic dependency installation. Please install manually.")


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

    script_dir = os.path.dirname(os.path.abspath(__file__))
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
    install_packages(distro, version) 

    install_path = os.path.join(script_dir, "Geant4", f"geant4-v{version}-install")
    print_info(f"Install path: {install_path}")

    instructions = f"""
[INSTRUCTIONS]
1. After CMake opens, it’ll greet you with an empty void labeled: EMPTY CACHE
   - Press 'c' to let it try configuring itself
   - Press 'e' to tell it, “Yes, I saw the warning, thank you, now go away”

2. Now tweak the settings like a responsible adult (use arrow keys to move around):
    – First stop: CMAKE_INSTALL_PREFIX. Hit Enter,
      then paste the path you actually want (Shift+Ctrl+V — not rocket science):
      {install_path}
      Hit Enter again. If it stops saying /usr/local, congrats, it worked.

3. Time to flip a few switches (don’t worry, no electrocution):
     Turn these ON unless you hate yourself later:
   - GEANT4_INSTALL_DATA
   - GEANT4_USE_OPENGL_X11
   - GEANT4_USE_QT
   - GEANT4_USE_RAYTRACER_X11
   (Feel free to turn on more — if you know what you’re doing or like surprises.)

4. Press 'c' again to configure your changes.
   - Keep pressing until it finally stops complaining and gives you a 'g'.

5. Smash 'g' to generate the Makefile.
   - That’s the thing that tells your computer how to build all this magic.

6. CMake will now vanish like a drama queen exiting stage left.
   - Get back to your terminal and continue the ride.
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
        geant4_examples_path = os.path.join(install_path, "share", "Geant4", "examples", "basic", "B1")
        user_example_path = os.path.expanduser("~/geant4-example-B1")
        build_path = os.path.join(user_example_path, "build")
        geant4_cmake_dir = os.path.join(install_path, "lib", "cmake", "Geant4")
        geant4_env_script = os.path.join(install_path, "bin", "geant4.sh")

        try:
            print_info("Copying Example B1 to a writable directory...")
            if os.path.exists(user_example_path):
                shutil.rmtree(user_example_path)
            shutil.copytree(geant4_examples_path, user_example_path)

            os.makedirs(build_path, exist_ok=True)
            os.chdir(build_path)

            cmake_command = f"cmake -DGeant4_DIR={geant4_cmake_dir} .."
            run_command(cmake_command, "Configuring Example B1")
            run_command(f"make -j{cores}", "Building Example B1")

            print_info("Running Example B1...")
            subprocess.run(f"bash -c 'source {geant4_env_script} && ./exampleB1'", shell=True, check=True)
            print_success("Example B1 ran successfully. Geant4 is working.")
        except Exception as e:
            print_error(f"Failed during Example B1 verification: {e}")
    else:
        print_success("Installation completed. You can manually test Geant4 later.")

if __name__ == "__main__":
    install_geant4()

