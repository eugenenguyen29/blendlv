"""Island terrain export module.

This module handles exporting island terrain meshes to GLB files.
Supports dual export modes:
- Merged: Single GLB per island containing all terrain (production)
- Individual: Separate GLB per terrain chunk (development/debugging)
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import bpy

from blender_extension.core.data import Island
from blender_extension.exporters.glb import export_objects_to_glb
from blender_extension.utils.files import get_export_subdir
from blender_extension.utils.naming import sanitize_name

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


def _export_individual_chunks(
    terrain_objects: list[bpy.types.Object],
    island: Island,
    terrain_dir: str,
    context: bpy.types.Context,
) -> tuple[list[str], None]:
    """Export each terrain object as separate GLB.

    Args:
        terrain_objects: List of terrain mesh objects to export.
        island: Island these objects belong to.
        terrain_dir: Directory to write GLB files.
        context: Blender context.

    Returns:
        Tuple of (chunk_paths, None) where chunk_paths are relative paths.
    """
    chunks: list[str] = []
    for obj in terrain_objects:
        chunk_name = sanitize_name(obj.name)
        filepath = os.path.join(terrain_dir, f"{chunk_name}.glb")
        if export_objects_to_glb([obj], filepath, context):
            chunks.append(f"islands/{island.id}/terrain/{chunk_name}.glb")
    return chunks, None


def _export_merged_terrain(
    terrain_objects: list[bpy.types.Object],
    island: Island,
    terrain_dir: str,
    context: bpy.types.Context,
) -> tuple[list[str], str | None]:
    """Export all terrain objects as single merged GLB.

    Args:
        terrain_objects: List of terrain mesh objects to export.
        island: Island these objects belong to.
        terrain_dir: Directory to write GLB file.
        context: Blender context.

    Returns:
        Tuple of ([], merged_path) where merged_path is relative path or None.
    """
    filepath = os.path.join(terrain_dir, "merged.glb")
    if export_objects_to_glb(terrain_objects, filepath, context):
        return [], f"islands/{island.id}/terrain/merged.glb"
    return [], None


def export_island_terrain(
    island: Island,
    export_path: str,
    context: bpy.types.Context,
    export_mode: str = "merged",
) -> tuple[list[str], str | None]:
    """Export terrain for a single island.

    Args:
        island: Island to export terrain for.
        export_path: Base export directory.
        context: Blender context.
        export_mode: "merged" (default) or "individual"

    Returns:
        Tuple of (chunk_paths, merged_path) where:
        - Individual mode: ([chunk1.glb, chunk2.glb, ...], None)
        - Merged mode: ([], "islands/{id}/terrain/merged.glb")
        - No terrain: ([], None)
    """
    terrain_objects = get_terrain_objects_for_island(island, context.scene)

    if not terrain_objects:
        return [], None

    terrain_dir = get_export_subdir(export_path, f"islands/{island.id}/terrain")

    if export_mode == "individual":
        return _export_individual_chunks(terrain_objects, island, terrain_dir, context)
    else:
        return _export_merged_terrain(terrain_objects, island, terrain_dir, context)


def export_islands(
    islands: dict[str, Island],
    export_path: str,
    context: bpy.types.Context,
    export_mode: str = "merged",
) -> dict[str, tuple[list[str], str | None]]:
    """Export terrain for all islands.

    Creates GLB files for each island's terrain in the islands/
    subdirectory structure.

    Args:
        islands: Dict of island_id to Island objects.
        export_path: Base export directory path.
        context: Blender context.
        export_mode: "merged" (default) or "individual"

    Returns:
        Dict mapping island_id to (chunks, merged) tuples.

    Directory Structure (individual mode):
        {export_path}/
        └── islands/
            └── {island_id}/
                └── terrain/
                    ├── chunk_a.glb
                    └── chunk_b.glb

    Directory Structure (merged mode):
        {export_path}/
        └── islands/
            └── {island_id}/
                └── terrain/
                    └── merged.glb
    """
    if not islands:
        return {}

    results: dict[str, tuple[list[str], str | None]] = {}

    for island_id, island in islands.items():
        chunks, merged = export_island_terrain(island, export_path, context, export_mode)
        results[island_id] = (chunks, merged)

    return results
