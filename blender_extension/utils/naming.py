"""Asset naming and sanitization utilities.

This module provides functions for generating consistent, safe names
for assets and instances that can be used as file names and identifiers.

Manual Test Checklist (Blender Python Console):
-----------------------------------------------
1. Test sanitize_name:
   >>> from blender_extension.utils.naming import sanitize_name
   >>> print(sanitize_name("My Object.001"))  # Should print: "my_object_001"
   >>> print(sanitize_name("Tree (Oak)"))     # Should print: "tree_oak"
   >>> print(sanitize_name("!!!"))            # Should print: "unnamed"
   >>> print(sanitize_name(""))               # Should print: "unnamed"

2. Test generate_asset_key with linked object:
   >>> from blender_extension.utils.naming import generate_asset_key
   >>> import bpy
   >>> obj = bpy.context.object
   >>> key = generate_asset_key(obj)
   >>> print(f"Asset key: {key}")

3. Test generate_instance_id:
   >>> from blender_extension.utils.naming import generate_instance_id
   >>> import bpy
   >>> obj = bpy.context.object
   >>> instance_id = generate_instance_id(obj)
   >>> print(f"Instance ID: {instance_id}")
"""

import os
import re
import unicodedata

import bpy

from blender_extension.utils.transforms import get_library_source


def sanitize_name(name: str) -> str:
    """Sanitize a name for use as file/asset identifier.

    Performs the following transformations:
    - Normalizes Unicode characters (NFD) and converts to ASCII
    - Converts to lowercase
    - Replaces spaces, dots, and hyphens with underscores
    - Removes special characters (keeps only alphanumeric and underscore)
    - Collapses multiple underscores to single
    - Strips leading/trailing underscores
    - Returns "unnamed" for empty results

    Args:
        name: Input name string to sanitize.

    Returns:
        Sanitized name safe for use as identifier or file name.

    Examples:
        >>> sanitize_name("My Object.001")
        'my_object_001'
        >>> sanitize_name("Tree (Oak)")
        'tree_oak'
        >>> sanitize_name("")
        'unnamed'
    """
    # Normalize Unicode (NFD) and convert to ASCII
    result = unicodedata.normalize("NFD", name)
    result = result.encode("ascii", "ignore").decode("ascii")

    # Lowercase
    result = result.lower()

    # Replace common separators
    result = result.replace(" ", "_")
    result = result.replace(".", "_")
    result = result.replace("-", "_")

    # Remove special characters, keep only alphanumeric and underscore
    result = re.sub(r"[^a-z0-9_]", "", result)

    # Collapse multiple underscores
    result = re.sub(r"_+", "_", result)

    # Strip leading/trailing underscores
    result = result.strip("_")

    return result or "unnamed"


def generate_asset_key(obj: bpy.types.Object) -> str:
    """Generate a unique asset key from an object.

    For linked objects, combines library name and mesh name.
    For local objects, uses the object name without numeric suffix.

    Args:
        obj: Blender object to generate key for.

    Returns:
        Sanitized asset key string.

    Examples:
        - Linked from trees.blend -> Oak_Tree.001 -> "trees_oak_tree"
        - Local mesh "House.002" -> "house"
    """
    source = get_library_source(obj)

    if source:
        # Extract library file name (without extension)
        lib_name = os.path.splitext(os.path.basename(source))[0]

        # Use mesh data name if available, otherwise object name
        mesh_name = obj.data.name if obj.data else obj.name

        # Remove numeric suffixes (.001, .002)
        mesh_name = re.sub(r"\.\d+$", "", mesh_name)

        key = f"{lib_name}_{mesh_name}"
    else:
        # Local object - use object name without numeric suffix
        key = re.sub(r"\.\d+$", "", obj.name)

    return sanitize_name(key)


def generate_instance_id(obj: bpy.types.Object) -> str:
    """Generate a unique instance ID for an object.

    Creates an ID by combining the sanitized object name with a short
    hash derived from the object's memory address. This ensures uniqueness
    even for objects with duplicate names within a Blender session.

    Args:
        obj: Blender object to generate ID for.

    Returns:
        Unique instance ID in format "{sanitized_name}_{hash}".

    Note:
        The hash is session-specific and will change between Blender sessions.
        For persistent IDs, use object custom properties.
    """
    base = sanitize_name(obj.name)

    # Add short hash from object's memory address for uniqueness
    # Blender objects have unique addresses during session
    obj_hash = hex(id(obj))[-6:]

    return f"{base}_{obj_hash}"
