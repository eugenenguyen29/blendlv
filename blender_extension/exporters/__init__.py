"""Exporters module - GLB export and manifest generation.

This module provides the main export functionality for the Trivesta Level
extension. It handles:

- Asset separation: Export unique assets to separate GLB files
- Island terrain: Export terrain meshes per island
- Collision meshes: Export collision geometry per island
- World elements: Export global elements (water, sky)
- Manifest v2.0: Generate JSON manifest with all metadata

Architecture:
    The export process is composed of focused sub-modules:
    - glb.py: Low-level GLB export helpers
    - assets.py: Asset separation and grouping
    - islands.py: Island terrain export
    - collision.py: Collision mesh export
    - world.py: World/global elements
    - manifest.py: v2.0 manifest serialization
"""

from __future__ import annotations

import os

import bpy

from blender_extension.core.data import ExportData
from blender_extension.entities import extract_all, register_extractors
from blender_extension.exporters.assets import export_assets
from blender_extension.exporters.base import (
    ExportResult,
    SelectionState,
    restore_selection,
    save_selection,
)
from blender_extension.exporters.collision import export_collision
from blender_extension.exporters.glb import (
    export_object_at_origin,
    export_objects_to_glb,
)
from blender_extension.exporters.islands import export_islands
from blender_extension.exporters.manifest import (
    ManifestSerializer,
    write_manifest,
)
from blender_extension.exporters.world import export_world_glb
from blender_extension.utils.collections import build_collection_tree
from blender_extension.utils.files import ensure_directory
from blender_extension.utils.islands import detect_islands


def export_world(
    context: bpy.types.Context,
    export_path: str,
) -> ExportResult:
    """Export the complete world with separated assets.

    This is the main export function that orchestrates the full export
    pipeline:
    1. Extract entity data from scene
    2. Detect islands
    3. Export unique assets to assets/
    4. Export island terrain to islands/
    5. Export collision meshes to collision/
    6. Export world elements to world.glb
    7. Generate manifest.json

    Args:
        context: Blender context.
        export_path: Base export directory (can use // for relative).

    Returns:
        ExportResult with success status, message, and file list.

    Output Structure:
        {export_path}/
        ├── manifest.json
        ├── world.glb
        ├── assets/
        │   └── {asset_id}.glb
        ├── islands/
        │   └── {island_id}.glb
        └── collision/
            └── {island_id}.glb
    """
    files_created: list[str] = []
    errors: list[str] = []

    try:
        # Ensure base directory exists
        abs_export_path = ensure_directory(export_path)

        # Register extractors (idempotent)
        register_extractors()

        # Extract scene data
        instances, terrain_objects, collision_objects = extract_all(context)

        # Detect islands
        islands = detect_islands(context.scene)

        # Build collection tree
        collection_tree = build_collection_tree(context.scene)

        # Create ExportData
        data = ExportData(
            instances=instances,
            terrain_objects=terrain_objects,
            islands=islands,
            collection_tree=collection_tree,
        )

        # Convert instance positions to island-local coordinates
        if islands:
            from blender_extension.utils.islands import convert_instances_to_local

            data.instances = convert_instances_to_local(data.instances, islands)

        # Build indices for efficient lookup
        data.build_indices()

        # Export assets
        asset_definitions = export_assets(instances, abs_export_path, context)
        data.asset_definitions = asset_definitions
        for asset_def in asset_definitions.values():
            files_created.append(os.path.join(abs_export_path, asset_def.file))

        # Export island terrain
        island_files = export_islands(islands, abs_export_path, context)
        for f in island_files:
            files_created.append(os.path.join(abs_export_path, f))

        # Export collision meshes
        collision_paths = export_collision(
            collision_objects, islands, abs_export_path, context
        )
        for island_id, path in collision_paths.items():
            files_created.append(os.path.join(abs_export_path, path))
            # Update island collision_mesh reference in our ExportData copy
            if island_id in data.islands:
                data.islands[island_id].collision_mesh = path

        # Export world elements
        world_files = export_world_glb(abs_export_path, context)
        for f in world_files:
            files_created.append(os.path.join(abs_export_path, f))

        # Write manifest
        manifest_success = write_manifest(data, abs_export_path, context)
        if manifest_success:
            files_created.append(os.path.join(abs_export_path, "manifest.json"))
        else:
            errors.append("Failed to write manifest.json")

        # Build result message
        total_instances = len(instances)
        total_assets = len(asset_definitions)
        total_islands = len(islands)
        message = (
            f"Exported {total_instances} instances, "
            f"{total_assets} assets, {total_islands} islands"
        )

        return ExportResult(
            success=len(errors) == 0,
            message=message,
            files_created=files_created,
            export_data=data,
            errors=errors,
        )

    except RuntimeError as e:
        return ExportResult(
            success=False,
            message=str(e),
            files_created=files_created,
            errors=[str(e)],
        )
    except Exception as e:
        return ExportResult(
            success=False,
            message=f"Export failed: {e}",
            files_created=files_created,
            errors=[str(e)],
        )


__all__ = [
    # Main export function
    "export_world",
    # Base types
    "ExportResult",
    "SelectionState",
    "save_selection",
    "restore_selection",
    # GLB helpers
    "export_objects_to_glb",
    "export_object_at_origin",
    # Sub-exporters
    "export_assets",
    "export_islands",
    "export_collision",
    "export_world_glb",
    # Manifest
    "ManifestSerializer",
    "write_manifest",
]
