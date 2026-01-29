"""Static mesh entity extractor.

This module provides the StaticExtractor class for extracting data from
regular static prop meshes. It serves as the default/fallback extractor
for mesh objects not handled by other specialized extractors.

Manual Test Checklist (Blender Python Console):
-----------------------------------------------
1. Test static mesh matching:
   >>> from blender_extension.entities.static import StaticExtractor
   >>> import bpy
   >>> ext = StaticExtractor()
   >>> bpy.ops.mesh.primitive_cube_add()
   >>> obj = bpy.context.object
   >>> print(ext.matches(obj))  # Should print True

2. Test extraction:
   >>> from blender_extension.entities.static import StaticExtractor
   >>> import bpy
   >>> ext = StaticExtractor()
   >>> obj = bpy.context.object
   >>> instance = ext.extract(obj)
   >>> print(f"Name: {instance.name}")
   >>> print(f"Entity type: {instance.entity_type}")
   >>> print(f"Position: {instance.position}")
"""

import bpy

from blender_extension.core.data import Instance
from blender_extension.entities.base import EntityExtractor
from blender_extension.utils.transforms import (
    get_bounding_box,
    get_custom_properties,
    get_object_transform,
)


class StaticExtractor(EntityExtractor):
    """Extractor for static prop meshes.

    Handles regular mesh objects that are not terrain or collision.
    This is the default/fallback extractor that matches any mesh object
    not explicitly marked as another type.

    Matching logic:
        - Must be a MESH type object
        - Not marked as terrain (trivesta.is_terrain = False)
        - Not marked as collision (trivesta.is_collision = False)
        - Legacy: Not marked with trivesta_is_terrain custom property

    Entity Type Override:
        If the object has trivesta.entity_type set to a custom value
        (e.g., 'npc', 'interactive'), that value is used instead of 'static'.
    """

    entity_type = "static"

    def matches(self, obj: bpy.types.Object) -> bool:
        """Match any mesh object not handled by other extractors.

        Args:
            obj: Blender object to check.

        Returns:
            True if object is a mesh without terrain/collision markers.
        """
        if obj.type != "MESH":
            return False

        # Check if explicitly marked as different type via properties
        if hasattr(obj, "trivesta"):
            if obj.trivesta.is_terrain or obj.trivesta.is_collision:
                return False

        # Check legacy property
        if obj.get("trivesta_is_terrain", False):
            return False

        return True

    def extract(self, obj: bpy.types.Object) -> Instance:
        """Extract static mesh instance data.

        Extracts transform, bounding box, and custom properties.
        Uses trivesta.entity_type if set, otherwise defaults to 'static'.

        Args:
            obj: Blender mesh object to extract from.

        Returns:
            Instance dataclass with extracted data.
        """
        transform = get_object_transform(obj)

        # Determine entity type from property or default
        entity_type = self.entity_type
        if hasattr(obj, "trivesta"):
            entity_type = obj.trivesta.entity_type

        return Instance(
            id=self._generate_instance_id(obj),
            name=obj.name,
            asset_id=self._generate_asset_key(obj),
            entity_type=entity_type,
            position=tuple(transform["position"]),
            rotation=tuple(transform["rotation"]),
            scale=tuple(transform["scale"]),
            bounding_box=get_bounding_box(obj),
            collection_path=self._get_collection_path(obj),
            custom_properties=get_custom_properties(obj),
        )
