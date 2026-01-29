"""Trivesta Level - Blender extension for Three.js level design.

This extension provides tools for exporting Blender scenes to Three.js compatible
formats, with support for asset separation, terrain detection, and collision meshes.
"""

bl_info = {
    "name": "Trivesta Level",
    "author": "Trivesta",
    "version": (2, 0, 0),
    "blender": (4, 2, 0),
    "location": "Properties > Scene > Trivesta Level",
    "description": "Export Three.js level geometry with asset separation",
    "category": "Import-Export",
}

import bpy

from .core.properties import register_properties, unregister_properties
from .core.registry import collect_classes
from .entities import register_extractors
from .panels.asset_browser import (
    register_asset_browser_properties,
    unregister_asset_browser_properties,
)


def register() -> None:
    """Register extension classes and properties."""
    try:
        for cls in collect_classes():
            bpy.utils.register_class(cls)
        register_properties()
        register_asset_browser_properties()
        register_extractors()
    except Exception as e:
        # Clean up any partial registration
        try:
            unregister()
        except Exception:
            pass
        raise RuntimeError(f"Failed to register Trivesta Level extension: {e}") from e


def unregister() -> None:
    """Unregister extension properties and classes."""
    try:
        unregister_asset_browser_properties()
    except Exception as e:
        print(f"Warning: Failed to unregister asset browser properties: {e}")

    try:
        unregister_properties()
    except Exception as e:
        print(f"Warning: Failed to unregister properties: {e}")

    for cls in reversed(collect_classes()):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print(f"Warning: Failed to unregister {cls.__name__}: {e}")


if __name__ == "__main__":
    register()
