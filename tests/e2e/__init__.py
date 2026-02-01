"""E2E test runner for Trivesta Level extension.

Run with:
    $BLENDER_EXE --background --factory-startup --python tests/e2e/__init__.py

Example:
    export BLENDER_EXE=/path/to/blender
    $BLENDER_EXE --background --factory-startup --python tests/e2e/__init__.py
"""

import sys
import unittest
from pathlib import Path

if __name__ == "__main__":
    # Add project root to sys.path so tests can import from tests.e2e.base
    project_root = str(Path(__file__).parent.parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Discover and run all tests in this directory
    loader = unittest.TestLoader()
    path = str(Path(__file__).parent)
    suite = loader.discover(path, pattern="test_*.py")

    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with appropriate exit code for CI/CD
    # Note: Using sys.exit() instead of bpy.ops.wm.quit_blender() because
    # sys.exit() properly propagates exit codes to the shell, which is
    # essential for CI/CD integration. bpy.ops.wm.quit_blender() does not
    # support custom exit codes.
    exit_code = 0 if result.wasSuccessful() else 1
    sys.exit(exit_code)
