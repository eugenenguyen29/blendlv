import os
import json
from datetime import datetime, timezone

import bpy
from bpy.types import Operator

from ..utils.transforms import (
    get_object_transform,
    get_bounding_box,
    get_custom_properties,
    get_library_source,
)


class TRIVESTA_OT_export_manifest(Operator):
    bl_idname = "trivesta.export_manifest"
    bl_label = "Export Manifest JSON"
    bl_description = "Export asset positions and metadata as JSON for developers"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.trivesta_level
        export_path = bpy.path.abspath(settings.export_path)

        # Ensure export directory exists
        os.makedirs(export_path, exist_ok=True)

        manifest_path = os.path.join(export_path, "manifest.json")

        # Collect asset data
        assets = []
        for obj in context.scene.objects:
            if obj.type != 'MESH':
                continue
            if not obj.visible_get():
                continue

            # Get library source for linked objects
            asset_file = get_library_source(obj)

            # Build asset entry
            asset_entry = {
                "name": obj.name,
                "asset_file": asset_file,
                **get_object_transform(obj),
                "bounding_box": get_bounding_box(obj),
                "custom_properties": get_custom_properties(obj),
            }

            # Add asset type if specified
            if "trivesta_asset_type" in obj:
                asset_entry["asset_type"] = obj["trivesta_asset_type"]

            assets.append(asset_entry)

        # Build manifest
        manifest = {
            "_generated": "AUTO-GENERATED FILE - DO NOT EDIT MANUALLY. Re-export from Blender instead.",
            "version": "1.0",
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "blender_file": bpy.data.filepath or "unsaved",
            "asset_count": len(assets),
            "assets": assets,
        }

        # Write JSON
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)

        self.report({'INFO'}, f"Exported manifest with {len(assets)} assets to {manifest_path}")
        return {'FINISHED'}
