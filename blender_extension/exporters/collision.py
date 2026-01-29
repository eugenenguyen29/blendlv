"""Collision mesh export module.

This module handles exporting collision meshes to separate GLB files.
Each island can have its own collision mesh exported to the collision/
subdirectory.

Manual Test Checklist (Blender Python Console):
-----------------------------------------------
1. Test export_collision:
   >>> from blender_extension.exporters.collision import export_collision
   >>> from blender_extension.entities import register_extractors, extract_all
   >>> from blender_extension.utils.islands import detect_islands
   >>> import bpy
   >>> register_extractors()
   >>> _, _, collision_objs = extract_all(bpy.context)
   >>> islands = detect_islands(bpy.context.scene)
   >>> paths = export_collision(collision_objs, islands, "/tmp/test_export/", bpy.context)
   >>> print(f"Exported {len(paths)} collision files")
   >>> for island_id, path in paths.items():
   ...     print(f"  {island_id}: {path}")

2. Test empty collision:
   >>> from blender_extension.exporters.collision import export_collision
   >>> import bpy
   >>> paths = export_collision([], {}, "/tmp/test_export/", bpy.context)
   >>> print(f"Paths: {len(paths)}")  # Should be 0

3. Test collision object detection:
   >>> from blender_extension.exporters.collision import find_island_for_object
   >>> from blender_extension.utils.islands import detect_islands
   >>> import bpy
   >>> islands = detect_islands(bpy.context.scene)
   >>> obj = bpy.context.object
   >>> if obj:
   ...     island_id = find_island_for_object(obj, islands, bpy.context.scene)
   ...     print(f"Object '{obj.name}' belongs to island: {island_id}")
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import bpy

from blender_extension.core.data import Instance, Island
from blender_extension.exporters.glb import export_objects_to_glb
from blender_extension.utils.files import get_export_subdir

if TYPE_CHECKING:
    pass


def find_island_for_object(
    obj: bpy.types.Object,
    islands: dict[str, Island],
    scene: bpy.types.Scene,
) -> str | None:
    """Find which island an object belongs to.

    Checks if the object is in any island's instance list.

    Args:
        obj: Object to find island for.
        islands: Dict of island_id to Island.
        scene: Blender scene (unused, kept for API consistency).

    Returns:
        Island ID if found, None otherwise.
    """
    for island_id, island in islands.items():
        if obj.name in island.instances:
            return island_id
    return None


def group_collision_by_island(
    collision_objects: list[Instance],
    islands: dict[str, Island],
    scene: bpy.types.Scene,
) -> dict[str, list[bpy.types.Object]]:
    """Group collision objects by their parent island.

    Args:
        collision_objects: List of collision Instance objects.
        islands: Dict of island_id to Island.
        scene: Blender scene to look up objects.

    Returns:
        Dict mapping island_id to list of collision mesh objects.
    """
    groups: dict[str, list[bpy.types.Object]] = {}

    for inst in collision_objects:
        obj = scene.objects.get(inst.name)
        if obj is None:
            continue

        island_id = find_island_for_object(obj, islands, scene)
        if island_id:
            groups.setdefault(island_id, []).append(obj)

    return groups


def export_collision(
    collision_objects: list[Instance],
    islands: dict[str, Island],
    export_path: str,
    context: bpy.types.Context,
) -> dict[str, str]:
    """Export collision meshes for all islands.

    Groups collision objects by island and exports combined collision
    GLB files for each island.

    Args:
        collision_objects: List of collision Instance objects.
        islands: Dict of island_id to Island objects (read-only, not mutated).
        export_path: Base export directory path.
        context: Blender context.

    Returns:
        Dict mapping island_id to relative file path. Callers should use this
        to update Island.collision_mesh references if needed.

    Note:
        This function does NOT mutate the islands dict. The caller is responsible
        for updating Island.collision_mesh references using the returned paths.

    Directory Structure:
        {export_path}/
        └── collision/
            ├── island_01.glb
            ├── island_02.glb
            └── ...
    """
    if not collision_objects or not islands:
        return {}

    # Create collision subdirectory
    collision_dir = get_export_subdir(export_path, "collision")

    # Group collision objects by island
    groups = group_collision_by_island(collision_objects, islands, context.scene)

    collision_paths: dict[str, str] = {}

    for island_id, objs in groups.items():
        if not objs:
            continue

        filename = f"{island_id}.glb"
        filepath = os.path.join(collision_dir, filename)

        success = export_objects_to_glb(objs, filepath, context)

        if success:
            relative_path = f"collision/{filename}"
            collision_paths[island_id] = relative_path
        else:
            print(
                f"[Collision Export Error] Failed to export collision mesh "
                f"for island '{island_id}'"
            )

    return collision_paths
