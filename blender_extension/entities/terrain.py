"""Terrain mesh entity extractor.

This module provides the TerrainExtractor class for extracting data from
terrain/ground meshes. Terrain objects are typically large, unique meshes
that define the walkable ground surface.

Manual Test Checklist (Blender Python Console):
-----------------------------------------------
1. Test terrain detection via property:
   >>> from blender_extension.entities.terrain import TerrainExtractor
   >>> import bpy
   >>> ext = TerrainExtractor()
   >>> bpy.ops.mesh.primitive_plane_add()
   >>> obj = bpy.context.object
   >>> obj.trivesta.is_terrain = True
   >>> print(ext.matches(obj))  # Should print True

2. Test terrain detection via legacy property:
   >>> from blender_extension.entities.terrain import TerrainExtractor
   >>> import bpy
   >>> ext = TerrainExtractor()
   >>> bpy.ops.mesh.primitive_plane_add()
   >>> obj = bpy.context.object
   >>> obj["trivesta_is_terrain"] = True
   >>> print(ext.matches(obj))  # Should print True

3. Test extraction (no asset_id):
   >>> from blender_extension.entities.terrain import TerrainExtractor
   >>> import bpy
   >>> ext = TerrainExtractor()
   >>> obj = bpy.context.object
   >>> obj.trivesta.is_terrain = True
   >>> instance = ext.extract(obj)
   >>> print(f"Asset ID: {instance.asset_id}")  # Should print None
   >>> print(f"Entity type: {instance.entity_type}")  # Should print terrain
"""

import bpy

from blender_extension.core.data import Instance
from blender_extension.entities.base import EntityExtractor
from blender_extension.utils.transforms import (
    get_bounding_box,
    get_custom_properties,
    get_object_transform,
)


class TerrainExtractor(EntityExtractor):
    """Extractor for terrain/ground meshes.

    Terrain objects are identified by explicit property markers.
    They are not instanced (asset_id is always None) because each
    terrain mesh is unique to its location.

    Matching logic (any of these):
        1. Object property: trivesta.is_terrain = True
        2. Object property: trivesta.entity_type = 'terrain'
        3. Legacy property: trivesta_is_terrain = True

    Important:
        Terrain is NOT auto-detected based on mesh size or library source.
        Objects must be explicitly marked as terrain.
    """

    entity_type = "terrain"

    def matches(self, obj: bpy.types.Object) -> bool:
        """Check if object is terrain.

        Args:
            obj: Blender object to check.

        Returns:
            True if object is explicitly marked as terrain.
        """
        if obj.type != "MESH":
            return False

        # Explicit terrain marking via is_terrain flag
        if hasattr(obj, "trivesta") and obj.trivesta.is_terrain:
            return True

        # Explicit terrain marking via entity_type
        if hasattr(obj, "trivesta") and obj.trivesta.entity_type == "terrain":
            return True

        # Legacy property
        if obj.get("trivesta_is_terrain", False):
            return True

        return False

    def extract(self, obj: bpy.types.Object) -> Instance:
        """Extract terrain instance data.

        Terrain objects have no asset_id because they are not instanced.
        Each terrain mesh is unique to its location.

        Args:
            obj: Blender mesh object to extract from.

        Returns:
            Instance dataclass with extracted data, asset_id=None.
        """
        transform = get_object_transform(obj)

        return Instance(
            id=self._generate_instance_id(obj),
            name=obj.name,
            asset_id=None,  # Terrain is not instanced
            entity_type=self.entity_type,
            position=tuple(transform["position"]),
            rotation=tuple(transform["rotation"]),
            scale=tuple(transform["scale"]),
            bounding_box=get_bounding_box(obj),
            collection_path=self._get_collection_path(obj),
            custom_properties=get_custom_properties(obj),
        )
