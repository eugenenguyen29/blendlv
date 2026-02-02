"""Utility to reliably find Blender executable.

Searches in order:
1. BLENDER_EXE environment variable
2. Common installation paths (platform-specific)
3. PATH lookup

Usage:
    from tests.e2e.find_blender import get_blender_path, run_e2e_tests

    # Get path only
    blender = get_blender_path()

    # Run E2E tests directly
    run_e2e_tests()
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def get_common_blender_paths() -> list[Path]:
    """Get common Blender installation paths for the current platform."""
    system = platform.system()
    paths: list[Path] = []

    if system == "Linux":
        paths = [
            # Snap installation (Ubuntu)
            Path("/snap/bin/blender"),
            # Flatpak
            Path("/var/lib/flatpak/exports/bin/org.blender.Blender"),
            Path.home() / ".local/share/flatpak/exports/bin/org.blender.Blender",
            # System package
            Path("/usr/bin/blender"),
            Path("/usr/local/bin/blender"),
            # Downloaded tarball (common locations)
            Path.home() / "blender/blender",
            Path.home() / "bin/blender",
            Path("/opt/blender/blender"),
            # Steam
            Path.home() / ".steam/steam/steamapps/common/Blender/blender",
        ]
    elif system == "Darwin":  # macOS
        paths = [
            Path("/Applications/Blender.app/Contents/MacOS/Blender"),
            Path.home() / "Applications/Blender.app/Contents/MacOS/Blender",
            Path("/usr/local/bin/blender"),
            # Homebrew
            Path("/opt/homebrew/bin/blender"),
        ]
    elif system == "Windows":
        # Common Windows paths
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
        paths = [
            Path(program_files) / "Blender Foundation" / "Blender 4.3" / "blender.exe",
            Path(program_files) / "Blender Foundation" / "Blender 4.2" / "blender.exe",
            Path(program_files) / "Blender Foundation" / "Blender 4.1" / "blender.exe",
            Path(program_files) / "Blender Foundation" / "Blender 4.0" / "blender.exe",
            Path(program_files_x86) / "Blender Foundation" / "Blender" / "blender.exe",
            # Steam
            Path(program_files_x86) / "Steam/steamapps/common/Blender/blender.exe",
        ]

    return paths


def get_blender_path() -> str | None:
    """Find Blender executable using multiple strategies.

    Returns:
        Path to Blender executable, or None if not found.

    Search order:
        1. BLENDER_EXE environment variable
        2. Common platform-specific installation paths
        3. PATH lookup via 'which blender' / shutil.which
    """
    # Strategy 1: Environment variable
    blender_exe = os.environ.get("BLENDER_EXE")
    if blender_exe and Path(blender_exe).exists():
        return blender_exe

    # Strategy 2: Common installation paths
    for path in get_common_blender_paths():
        if path.exists() and path.is_file():
            return str(path)

    # Strategy 3: PATH lookup
    blender_in_path = shutil.which("blender")
    if blender_in_path:
        return blender_in_path

    return None


def get_blender_version(blender_path: str) -> str | None:
    """Get Blender version string.

    Args:
        blender_path: Path to Blender executable

    Returns:
        Version string like "4.3.0" or None if failed
    """
    try:
        result = subprocess.run(
            [blender_path, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Parse "Blender 4.3.0" from output
        for line in result.stdout.split("\n"):
            if line.startswith("Blender "):
                return line.split()[1]
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None


def run_e2e_tests(verbose: bool = True) -> int:
    """Run E2E tests using discovered Blender executable.

    Args:
        verbose: Print status messages

    Returns:
        Exit code (0 = success, 1 = failure, 2 = Blender not found)
    """
    blender = get_blender_path()

    if not blender:
        if verbose:
            print("ERROR: Blender executable not found.")
            print("")
            print("Searched in:")
            print("  1. BLENDER_EXE environment variable")
            print("  2. Common installation paths:")
            for path in get_common_blender_paths():
                print(f"     - {path}")
            print("  3. System PATH")
            print("")
            print("Solutions:")
            print("  - Set BLENDER_EXE: export BLENDER_EXE=/path/to/blender")
            print("  - Install Blender and ensure it's in PATH")
            print("  - On Ubuntu: sudo snap install blender --classic")
        return 2

    if verbose:
        version = get_blender_version(blender)
        print(f"Found Blender: {blender}")
        if version:
            print(f"Version: {version}")
        print("")

    # Get path to test runner
    test_runner = Path(__file__).parent / "__init__.py"

    # Run tests
    cmd = [
        blender,
        "--background",
        "--factory-startup",
        "--python",
        str(test_runner),
    ]

    if verbose:
        print(f"Running: {' '.join(cmd)}")
        print("-" * 60)

    result = subprocess.run(cmd)
    return result.returncode


if __name__ == "__main__":
    # When run directly, execute E2E tests
    sys.exit(run_e2e_tests())
