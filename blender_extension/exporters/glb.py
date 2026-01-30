"""GLB export helper functions.

This module provides low-level GLB export functionality using Blender's
glTF exporter with correct settings for Three.js (Y-up coordinate system).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import bpy

from blender_extension.exporters.base import restore_selection, save_selection

if TYPE_CHECKING:
    pass


def export_objects_to_glb(
    objects: list[bpy.types.Object],
    filepath: str,
    context: bpy.types.Context,
) -> bool:
    """Export multiple objects to a GLB file.

    Selects the given objects and exports them using Blender's glTF
    exporter with settings optimized for Three.js.

    Args:
        objects: List of Blender objects to export.
        filepath: Absolute path for output GLB file.
        context: Blender context.

    Returns:
        True if export succeeded, False otherwise.

    Note:
        Selection state is preserved - original selection is restored
        after export completes.
    """
    if not objects:
        return False

    # Save selection state
    saved = save_selection(context)

    try:
        # Select only export objects
        bpy.ops.object.select_all(action="DESELECT")
        for obj in objects:
            obj.select_set(True)

        # Export with Three.js-compatible settings
        bpy.ops.export_scene.gltf(
            filepath=filepath,
            use_selection=True,
            export_format="GLB",
            export_apply=True,
            export_texcoords=True,
            export_normals=True,
            export_materials="EXPORT",
            export_yup=True,  # Three.js uses Y-up
        )
        return True

    except Exception as e:
        print(f"[GLB Export Error] Failed to export objects to '{filepath}': {e}")
        return False

    finally:
        # Restore selection
        restore_selection(context, saved)


def export_object_at_origin(
    obj: bpy.types.Object,
    filepath: str,
    context: bpy.types.Context,
) -> bool:
    """Export a single object centered at world origin.

    Temporarily moves the object to origin, exports it, then restores
    its original position. This is used for asset exports where the
    geometry should be centered.

    Args:
        obj: Blender object to export.
        filepath: Absolute path for output GLB file.
        context: Blender context.

    Returns:
        True if export succeeded, False otherwise.

    Note:
        The object's transform is temporarily modified during export
        but is restored afterwards.
    """
    if obj is None:
        return False

    # Save selection state
    saved = save_selection(context)

    # Store original transform
    original_location = obj.location.copy()

    try:
        # Move to origin for export
        obj.location = (0, 0, 0)

        # Select only this object
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)

        # Export with Three.js-compatible settings
        bpy.ops.export_scene.gltf(
            filepath=filepath,
            use_selection=True,
            export_format="GLB",
            export_apply=True,
            export_texcoords=True,
            export_normals=True,
            export_materials="EXPORT",
            export_yup=True,
        )
        return True

    except Exception as e:
        print(
            f"[GLB Export Error] Failed to export object '{obj.name}' "
            f"at origin to '{filepath}': {e}"
        )
        return False

    finally:
        # Always restore original transform even on exception
        obj.location = original_location
        # Restore selection
        restore_selection(context, saved)
