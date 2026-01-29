"""File and path handling utilities.

This module provides functions for path resolution and directory management,
with support for Blender's relative path notation (//).

Manual Test Checklist (Blender Python Console):
-----------------------------------------------
1. Test resolve_path:
   >>> from blender_extension.utils.files import resolve_path
   >>> abs_path = resolve_path("//exports/")
   >>> print(f"Absolute: {abs_path}")

2. Test ensure_directory:
   >>> from blender_extension.utils.files import ensure_directory
   >>> path = ensure_directory("//exports/test/")
   >>> print(f"Created: {path}")

3. Test get_relative_path:
   >>> from blender_extension.utils.files import get_relative_path
   >>> rel = get_relative_path("/home/user/exports/assets/tree.glb", "/home/user/exports")
   >>> print(f"Relative: {rel}")  # Should print: assets/tree.glb

4. Test get_export_subdir:
   >>> from blender_extension.utils.files import get_export_subdir
   >>> subdir = get_export_subdir("//exports/", "assets")
   >>> print(f"Subdir: {subdir}")
"""

import os

import bpy


def resolve_path(path: str) -> str:
    """Resolve a path, handling Blender's // relative notation.

    Blender uses // as a prefix to indicate paths relative to the
    current .blend file. This function converts such paths to absolute.

    Args:
        path: Path string (absolute or Blender relative with //).

    Returns:
        Absolute path string.

    Examples:
        >>> resolve_path("//exports/")
        '/home/user/project/exports/'
        >>> resolve_path("/absolute/path")
        '/absolute/path'
    """
    return bpy.path.abspath(path)


def ensure_directory(path: str) -> str:
    """Ensure a directory exists, creating it if necessary.

    Creates the directory and all parent directories if they don't exist.
    Handles Blender's // relative path notation.

    Args:
        path: Directory path (can be Blender relative //).

    Returns:
        Absolute path to the directory.

    Raises:
        RuntimeError: If path uses // notation but .blend file is not saved.
        OSError: If directory creation fails due to permissions or other issues.
    """
    if path.startswith("//") and not bpy.data.filepath:
        raise RuntimeError(
            "Cannot resolve relative path '//': .blend file is not saved. "
            "Please save the file first."
        )
    abs_path = resolve_path(path)
    os.makedirs(abs_path, exist_ok=True)
    return abs_path


def get_relative_path(absolute_path: str, base_path: str) -> str:
    """Get a path relative to a base directory.

    Computes the relative path from base_path to absolute_path.

    Args:
        absolute_path: Full path to file or directory.
        base_path: Base directory path to compute relative from.

    Returns:
        Relative path string (e.g., "assets/tree.glb").

    Examples:
        >>> get_relative_path("/home/user/exports/assets/tree.glb", "/home/user/exports")
        'assets/tree.glb'
    """
    return os.path.relpath(absolute_path, base_path)


def get_export_subdir(base_path: str, subdir: str) -> str:
    """Get a subdirectory path within export directory.

    Creates the subdirectory if it doesn't exist.

    Args:
        base_path: Base export path (can be Blender relative //).
        subdir: Subdirectory name (e.g., "assets", "islands").

    Returns:
        Absolute path to subdirectory (created if needed).

    Examples:
        >>> get_export_subdir("//exports/", "assets")
        '/home/user/project/exports/assets'
    """
    path = os.path.join(resolve_path(base_path), subdir)
    os.makedirs(path, exist_ok=True)
    return path
