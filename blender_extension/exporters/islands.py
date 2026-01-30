"""Island terrain export module.

This module handles exporting island terrain meshes to separate GLB files.
Each island gets its own terrain GLB file in the islands/ subdirectory.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import bpy

from blender_extension.core.data import Island
from blender_extension.exporters.glb import export_objects_to_glb
from blender_extension.utils.files import get_export_subdir

if TYPE_CHECKING:
    pass


def get_terrain_objects_for_island(
    island: Island,
    scene: bpy.types.Scene,
) -> list[bpy.types.Object]:
    """Get terrain objects belonging to an island.

    Finds terrain objects by checking if they are in the island's
    terrain_objects list or match naming conventions.

    Args:
        island: Island to get terrain for.
        scene: Blender scene to search.

    Returns:
        List of terrain mesh objects.
    """
    terrain_objects = []

    # Get objects from terrain_objects list
    for obj_name in island.terrain_objects:
        obj = scene.objects.get(obj_name)
        if obj and obj.type == "MESH":
            terrain_objects.append(obj)

    # If no explicit terrain objects, look for terrain in island
    if not terrain_objects:
        # Get all objects in the island
        for obj_name in island.instances:
            obj = scene.objects.get(obj_name)
            if obj and obj.type == "MESH":
                # Check for terrain naming convention
                name_lower = obj.name.lower()
                if "terrain" in name_lower or "ground" in name_lower:
                    terrain_objects.append(obj)

    return terrain_objects


def export_island_terrain(
    island: Island,
    islands_dir: str,
    context: bpy.types.Context,
) -> str | None:
    """Export terrain for a single island.

    Args:
        island: Island to export terrain for.
        islands_dir: Directory to write GLB file.
        context: Blender context.

    Returns:
        Relative path to exported file, or None if no terrain exported.
    """
    terrain_objects = get_terrain_objects_for_island(island, context.scene)

    if not terrain_objects:
        return None

    filename = f"{island.id}.glb"
    filepath = os.path.join(islands_dir, filename)

    success = export_objects_to_glb(terrain_objects, filepath, context)

    if success:
        return f"islands/{filename}"
    return None


def export_islands(
    islands: dict[str, Island],
    export_path: str,
    context: bpy.types.Context,
) -> list[str]:
    """Export terrain for all islands.

    Creates GLB files for each island's terrain in the islands/
    subdirectory.

    Args:
        islands: Dict of island_id to Island objects.
        export_path: Base export directory path.
        context: Blender context.

    Returns:
        List of created file paths (relative to export_path).

    Directory Structure:
        {export_path}/
        └── islands/
            ├── island_01.glb
            ├── island_02.glb
            └── ...
    """
    if not islands:
        return []

    # Create islands subdirectory
    islands_dir = get_export_subdir(export_path, "islands")

    files_created: list[str] = []

    for island in islands.values():
        path = export_island_terrain(island, islands_dir, context)
        if path:
            files_created.append(path)

    return files_created
