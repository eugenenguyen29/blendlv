"""World/global elements export module.

This module handles exporting world-level elements that are not part of
any specific island, such as water planes, skyboxes, or global decorations.

Manual Test Checklist (Blender Python Console):
-----------------------------------------------
1. Test export_world_glb:
   >>> from blender_extension.exporters.world import export_world_glb
   >>> import bpy
   >>> files = export_world_glb("/tmp/test_export/", bpy.context)
   >>> print(f"Exported {len(files)} world files")

2. Test get_world_objects:
   >>> from blender_extension.exporters.world import get_world_objects
   >>> import bpy
   >>> objs = get_world_objects(bpy.context.scene)
   >>> print(f"Found {len(objs)} world objects")
   >>> for obj in objs:
   ...     print(f"  {obj.name}")
"""

import os
from typing import TYPE_CHECKING

import bpy

from blender_extension.exporters.glb import export_objects_to_glb
from blender_extension.utils.files import ensure_directory

if TYPE_CHECKING:
    pass


def get_world_objects(scene: bpy.types.Scene) -> list[bpy.types.Object]:
    """Get objects that are world-level (not in Island_ collections).

    Finds visible mesh objects that should be exported as part of the
    world GLB, such as water planes or skybox elements.

    Args:
        scene: Blender scene to search.

    Returns:
        List of world-level mesh objects.
    """
    world_objects = []

    for obj in scene.objects:
        if obj.type != "MESH" or not obj.visible_get():
            continue

        # Skip manifest-only objects
        if obj.get("trivesta_manifest_only", False):
            continue

        # Check if object is in an Island_ collection
        is_in_island = False
        for collection in obj.users_collection:
            # Walk up collection hierarchy
            current = collection
            while current:
                if current.name.startswith("Island_"):
                    is_in_island = True
                    break
                # Find parent collection
                parent = None
                for scene_coll in bpy.data.scenes:
                    for coll in scene_coll.collection.children_recursive:
                        if current in coll.children[:]:
                            parent = coll
                            break
                current = parent

            if is_in_island:
                break

        if not is_in_island:
            # Check naming conventions for world objects
            name_lower = obj.name.lower()
            if any(
                kw in name_lower
                for kw in ["water", "ocean", "sky", "sun", "moon", "cloud", "global"]
            ):
                world_objects.append(obj)

    return world_objects


def export_world_glb(
    export_path: str,
    context: bpy.types.Context,
) -> list[str]:
    """Export world-level elements to world.glb.

    Exports global elements like water planes and skybox elements
    that are not part of any specific island.

    Args:
        export_path: Base export directory path.
        context: Blender context.

    Returns:
        List of created file paths (relative to export_path).
    """
    # Ensure export directory exists
    abs_path = ensure_directory(export_path)

    world_objects = get_world_objects(context.scene)

    if not world_objects:
        return []

    filepath = os.path.join(abs_path, "world.glb")

    success = export_objects_to_glb(world_objects, filepath, context)

    if success:
        return ["world.glb"]
    return []
