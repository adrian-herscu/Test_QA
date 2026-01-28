#!/usr/bin/env python3
# pyright: ignore
"""
Development environment setup script for the Ammeter Testing Framework.

This script automatically sets up a virtual environment and installs the project
in development mode. It works on Windows, macOS, and Linux.

Usage:
    python setup_dev.py
"""

import os
import sys
import subprocess
import venv
from pathlib import Path


def check_python_version():
    """Verify Python 3.10+ is being used."""
    if sys.version_info < (3, 10):
        print("❌ Error: Python 3.10 or higher is required.")
        print(f"   Current version: {sys.version}")
        print("\nPlease install Python 3.10+ and try again.")
        sys.exit(1)
    print(
        f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected")


def get_venv_path():
    """Get the path to the virtual environment."""
    return Path(".venv")


def create_venv(venv_path):
    """Create a virtual environment if it doesn't exist."""
    if venv_path.exists():
        print(f"✓ Virtual environment already exists at {venv_path}")
        return True

    print(f"\nCreating virtual environment at {venv_path}...")
    try:
        venv.create(venv_path, with_pip=True)
        print(f"✓ Virtual environment created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False


def get_pip_command(venv_path):
    """Get the pip command for the virtual environment."""
    if sys.platform == "win32":
        return venv_path / "Scripts" / "pip"
    else:
        return venv_path / "bin" / "pip"


def get_python_command(venv_path):
    """Get the python command for the virtual environment."""
    if sys.platform == "win32":
        return venv_path / "Scripts" / "python"
    else:
        return venv_path / "bin" / "python"


def upgrade_pip(pip_cmd):
    """Upgrade pip to the latest version."""
    print("\nUpgrading pip...")
    try:
        subprocess.run(
            [str(pip_cmd), "install", "--upgrade", "pip"],
            check=True,
            capture_output=True
        )
        print("✓ pip upgraded successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to upgrade pip: {e}")
        print(f"   stdout: {e.stdout.decode() if e.stdout else 'N/A'}")
        print(f"   stderr: {e.stderr.decode() if e.stderr else 'N/A'}")
        return False


def install_project(pip_cmd):
    """Install the project in editable mode."""
    print("\nInstalling project in editable mode...")
    try:
        subprocess.run(
            [str(pip_cmd), "install", "-e", "."],
            check=True
        )
        print("✓ Project installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install project: {e}")
        return False


def print_activation_instructions(venv_path):
    """Print instructions for activating the virtual environment."""
    print("\n" + "=" * 70)
    print("✓ Setup complete!")
    print("=" * 70)
    print("\nTo activate the virtual environment, run:\n")

    if sys.platform == "win32":
        print(f"  .venv\\Scripts\\activate")
    else:
        print(f"  source .venv/bin/activate")

    print("\nThen you can run:")
    print("  python examples/run_emulators.py    # Start ammeter emulators")
    print("  python examples/run_tests.py         # Run test framework")
    print("  python examples/error_simulation_demo.py  # Test error handling")
    print("  python examples/ammeter_comparison.py    # Compare results")
    print("\nOr run unit tests:")
    print("  python -m unittest tests/test_cases.py")
    print("\n" + "=" * 70)


def main():
    """Main setup routine."""
    print("=" * 70)
    print("Ammeter Testing Framework - Development Setup")
    print("=" * 70)

    # Check Python version
    print("\nChecking Python version...")
    check_python_version()

    # Get venv path
    venv_path = get_venv_path()

    # Create virtual environment
    if not create_venv(venv_path):
        sys.exit(1)

    # Get pip command
    pip_cmd = get_pip_command(venv_path)

    # Upgrade pip
    if not upgrade_pip(pip_cmd):
        print("\n⚠️  Warning: pip upgrade had issues, but continuing...")

    # Install project
    if not install_project(pip_cmd):
        sys.exit(1)

    # Print activation instructions
    print_activation_instructions(venv_path)


if __name__ == "__main__":
    main()
