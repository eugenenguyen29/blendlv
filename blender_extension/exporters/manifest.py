"""Manifest v2.0 serializer.

This module handles serialization and writing of the v2.0 manifest format.
The manifest contains all metadata needed by the Three.js runtime to load
and instantiate the game world.

Manual Test Checklist (Blender Python Console):
-----------------------------------------------
1. Test ManifestSerializer:
   >>> from blender_extension.exporters.manifest import ManifestSerializer
   >>> from blender_extension.core.data import ExportData
   >>> import bpy
   >>> serializer = ManifestSerializer()
   >>> data = ExportData()
   >>> manifest = serializer.serialize(data, bpy.context)
   >>> print(f"Version: {manifest['version']}")
   >>> print(f"Keys: {list(manifest.keys())}")

2. Test with populated data:
   >>> from blender_extension.exporters.manifest import ManifestSerializer
   >>> from blender_extension.entities import register_extractors, extract_all
   >>> from blender_extension.utils.islands import detect_islands
   >>> from blender_extension.utils.collections import build_collection_tree
   >>> from blender_extension.core.data import ExportData
   >>> import bpy
   >>> register_extractors()
   >>> instances, terrain, collision = extract_all(bpy.context)
   >>> data = ExportData(
   ...     instances=instances,
   ...     terrain_objects=terrain,
   ...     islands=detect_islands(bpy.context.scene),
   ...     collection_tree=build_collection_tree(bpy.context.scene),
   ... )
   >>> data.build_indices()
   >>> serializer = ManifestSerializer()
   >>> manifest = serializer.serialize(data, bpy.context)
   >>> print(f"Instances: {len(manifest['instances'])}")

3. Test write_manifest:
   >>> from blender_extension.exporters.manifest import write_manifest
   >>> from blender_extension.core.data import ExportData
   >>> import bpy
   >>> data = ExportData()
   >>> success = write_manifest(data, "/tmp/test_export/", bpy.context)
   >>> print(f"Write success: {success}")
"""

import json
import os
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

import bpy

from blender_extension.core.constants import MANIFEST_VERSION
from blender_extension.core.data import (
    AssetDefinition,
    CollectionNode,
    ExportData,
    Instance,
    Island,
)
from blender_extension.utils.files import ensure_directory

if TYPE_CHECKING:
    pass


class ManifestSerializer:
    """Serializer for v2.0 manifest format.

    Converts ExportData into a JSON-serializable dictionary
    following the v2.0 manifest schema.
    """

    def serialize(
        self,
        data: ExportData,
        context: bpy.types.Context,
    ) -> dict[str, Any]:
        """Serialize ExportData to manifest dictionary.

        Args:
            data: ExportData containing all export information.
            context: Blender context for scene information.

        Returns:
            JSON-serializable dictionary matching v2.0 schema.
        """
        return {
            "_generated": (
                "AUTO-GENERATED FILE - DO NOT EDIT MANUALLY. "
                "Re-export from Blender instead."
            ),
            "version": MANIFEST_VERSION,
            "exported_at": datetime.now(UTC).isoformat(),
            "blender_file": bpy.data.filepath or "unsaved",
            "asset_definitions": self._serialize_asset_definitions(
                data.asset_definitions
            ),
            "instances": self._serialize_instances(data.instances),
            "terrain_objects": self._serialize_instances(data.terrain_objects),
            "collections": self._serialize_collection_tree(data.collection_tree),
            "islands": self._serialize_islands(data.islands),
            "world": self._serialize_world(context),
            "statistics": self._compute_statistics(data),
        }

    def _serialize_asset_definitions(
        self,
        definitions: dict[str, AssetDefinition],
    ) -> dict[str, dict[str, Any]]:
        """Serialize asset definitions.

        Args:
            definitions: Dict of asset_id to AssetDefinition.

        Returns:
            Serialized asset definitions.
        """
        result = {}
        for asset_id, asset_def in definitions.items():
            result[asset_id] = {
                "id": asset_def.id,
                "file": asset_def.file,
            }
            if asset_def.source:
                result[asset_id]["source"] = asset_def.source
        return result

    def _serialize_instances(
        self,
        instances: list[Instance],
    ) -> list[dict[str, Any]]:
        """Serialize instance list.

        Args:
            instances: List of Instance objects.

        Returns:
            List of serialized instance dictionaries.
        """
        return [self._serialize_instance(inst) for inst in instances]

    def _serialize_instance(self, inst: Instance) -> dict[str, Any]:
        """Serialize a single instance.

        Args:
            inst: Instance to serialize.

        Returns:
            Serialized instance dictionary.
        """
        result: dict[str, Any] = {
            "id": inst.id,
            "name": inst.name,
            "entity_type": inst.entity_type,
            "position": list(inst.position),
            "rotation": list(inst.rotation),
            "scale": list(inst.scale),
            "bounding_box": inst.bounding_box,
            "collection_path": inst.collection_path,
        }
        if inst.asset_id:
            result["asset_id"] = inst.asset_id
        if inst.custom_properties:
            result["custom_properties"] = inst.custom_properties
        return result

    def _serialize_collection_tree(
        self,
        tree: CollectionNode | None,
    ) -> dict[str, Any] | None:
        """Serialize collection hierarchy.

        Args:
            tree: Root CollectionNode or None.

        Returns:
            Serialized tree dictionary or None.
        """
        if tree is None:
            return None
        return tree.to_dict()

    def _serialize_islands(
        self,
        islands: dict[str, Island],
    ) -> dict[str, dict[str, Any]]:
        """Serialize island definitions.

        Args:
            islands: Dict of island_id to Island.

        Returns:
            Serialized islands dictionary.
        """
        result = {}
        for island_id, island in islands.items():
            result[island_id] = {
                "id": island.id,
                "name": island.name,
                "world_position": list(island.world_position),
                "world_rotation": list(island.world_rotation),
                "bounds": island.bounds,
                "instances": island.instances,
                "terrain_objects": island.terrain_objects,
            }
            if island.collision_mesh:
                result[island_id]["collision_mesh"] = island.collision_mesh
        return result

    def _serialize_world(
        self,
        context: bpy.types.Context,
    ) -> dict[str, Any]:
        """Serialize world-level data.

        Args:
            context: Blender context to read scene settings.

        Returns:
            World metadata dictionary with size and water level.
        """
        settings = context.scene.trivesta
        return {
            "file": "world.glb",
            "size": [settings.world_size_x, settings.world_size_z],
            "water_level": settings.water_level,
        }

    def _compute_statistics(self, data: ExportData) -> dict[str, int]:
        """Compute export statistics.

        Args:
            data: ExportData to compute stats from.

        Returns:
            Statistics dictionary.
        """
        return {
            "total_instances": len(data.instances),
            "total_terrain": len(data.terrain_objects),
            "total_assets": len(data.asset_definitions),
            "total_islands": len(data.islands),
        }


def write_manifest(
    data: ExportData,
    export_path: str,
    context: bpy.types.Context,
) -> bool:
    """Write manifest.json to export directory.

    Args:
        data: ExportData to serialize.
        export_path: Base export directory path.
        context: Blender context.

    Returns:
        True if write succeeded, False otherwise.
    """
    try:
        abs_path = ensure_directory(export_path)
        filepath = os.path.join(abs_path, "manifest.json")

        serializer = ManifestSerializer()
        manifest = serializer.serialize(data, context)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return True
    except Exception as e:
        error_msg = f"Failed to write manifest to '{export_path}': {e}"
        print(f"[Manifest Export Error] {error_msg}")
        raise RuntimeError(error_msg) from e
