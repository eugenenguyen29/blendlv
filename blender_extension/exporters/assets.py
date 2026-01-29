"""Asset export module.

This module handles exporting unique assets (shared geometry) to separate
GLB files. Assets are grouped by asset_id, and each unique asset is exported
once to the assets/ subdirectory.

Manual Test Checklist (Blender Python Console):
-----------------------------------------------
1. Test export_assets with instances:
   >>> from blender_extension.exporters.assets import export_assets
   >>> from blender_extension.entities import register_extractors, extract_all
   >>> from blender_extension.core.data import ExportData
   >>> import bpy
   >>> register_extractors()
   >>> instances, terrain, collision = extract_all(bpy.context)
   >>> assets = export_assets(instances, "/tmp/test_export/", bpy.context)
   >>> print(f"Exported {len(assets)} assets")
   >>> for key, asset_def in assets.items():
   ...     print(f"  {key}: {asset_def.file}")

2. Test empty instances list:
   >>> from blender_extension.exporters.assets import export_assets
   >>> import bpy
   >>> assets = export_assets([], "/tmp/test_export/", bpy.context)
   >>> print(f"Assets: {len(assets)}")  # Should be 0

3. Test asset grouping:
   >>> from blender_extension.exporters.assets import group_by_asset_id
   >>> from blender_extension.entities import register_extractors, extract_all
   >>> import bpy
   >>> register_extractors()
   >>> instances, _, _ = extract_all(bpy.context)
   >>> groups = group_by_asset_id(instances)
   >>> for asset_id, insts in groups.items():
   ...     print(f"  {asset_id}: {len(insts)} instances")
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import bpy

from blender_extension.core.data import AssetDefinition, Instance
from blender_extension.exporters.glb import export_object_at_origin
from blender_extension.utils.files import get_export_subdir

if TYPE_CHECKING:
    pass


def group_by_asset_id(instances: list[Instance]) -> dict[str, list[Instance]]:
    """Group instances by their asset_id.

    Instances with the same asset_id share geometry and should use
    the same GLB file.

    Args:
        instances: List of Instance objects.

    Returns:
        Dict mapping asset_id to list of instances sharing that asset.
    """
    groups: dict[str, list[Instance]] = {}
    for inst in instances:
        if inst.asset_id:
            groups.setdefault(inst.asset_id, []).append(inst)
    return groups


def find_object_by_name(
    scene: bpy.types.Scene, name: str
) -> bpy.types.Object | None:
    """Find an object in the scene by name.

    Args:
        scene: Blender scene to search.
        name: Object name to find.

    Returns:
        The object if found, None otherwise.
    """
    return scene.objects.get(name)


def export_assets(
    instances: list[Instance],
    export_path: str,
    context: bpy.types.Context,
) -> dict[str, AssetDefinition]:
    """Export unique assets to GLB files.

    Groups instances by asset_id and exports each unique asset once
    to the assets/ subdirectory. Returns asset definitions that map
    asset IDs to their GLB file paths.

    Args:
        instances: List of Instance objects to export assets from.
        export_path: Base export directory path.
        context: Blender context.

    Returns:
        Dict mapping asset_id to AssetDefinition with file paths.

    Directory Structure:
        {export_path}/
        └── assets/
            ├── {asset_id_1}.glb
            ├── {asset_id_2}.glb
            └── ...
    """
    if not instances:
        return {}

    # Create assets subdirectory
    assets_dir = get_export_subdir(export_path, "assets")

    # Group by asset_id
    groups = group_by_asset_id(instances)

    asset_definitions: dict[str, AssetDefinition] = {}

    for asset_id, inst_group in groups.items():
        if not inst_group:
            continue

        # Use first instance to find the object
        first_inst = inst_group[0]
        obj = find_object_by_name(context.scene, first_inst.name)

        if obj is None:
            continue

        # Determine output path
        filename = f"{asset_id}.glb"
        filepath = os.path.join(assets_dir, filename)

        # Export the object at origin
        success = export_object_at_origin(obj, filepath, context)

        if success:
            # Get source library path if linked
            source = None
            if obj.library:
                source = obj.library.filepath
            elif obj.data and obj.data.library:
                source = obj.data.library.filepath
            elif obj.override_library and obj.override_library.reference:
                ref = obj.override_library.reference
                if ref.library:
                    source = ref.library.filepath

            asset_definitions[asset_id] = AssetDefinition(
                id=asset_id,
                file=f"assets/{filename}",
                source=source,
            )

    return asset_definitions
