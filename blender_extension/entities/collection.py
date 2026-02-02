"""Collection instance entity extractor.

This module provides the CollectionExtractor class for extracting data from
collection instances (Empties with instance_type='COLLECTION').

Collection instances are created when placing collections from the Asset Shelf.
They are EMPTY objects that reference a collection, allowing the same group of
objects to be instanced multiple times in a scene.
"""

from __future__ import annotations

import math
import os

import bpy

from blender_extension.core.data import BoundingBox, Instance
from blender_extension.entities.base import EntityExtractor
from blender_extension.utils.naming import sanitize_name
from blender_extension.utils.transforms import (
    get_custom_properties,
    get_object_transform,
)


class CollectionExtractor(EntityExtractor):
    """Extractor for collection instances.

    Handles EMPTY objects that instance collections (placed via Asset Shelf).
    These represent groups of objects treated as a single placeable asset.

    Matching logic:
        - Must be an EMPTY type object
        - Must have instance_type == 'COLLECTION'
        - Must have a valid instance_collection reference

    Entity Type Override:
        If the object has trivesta.entity_type set, that value is used.
        Otherwise defaults to 'static'.

    NPC Dialog Serialization:
        For NPC entities (entity_type='npc'), serializes dialog_lines into
        custom_properties["dialog"].

    Interactive Serialization:
        For Interactive entities (entity_type='interactive'), serializes
        script_id into custom_properties["script_id"].

    Asset Key Generation:
        - Linked collection: {library_name}_{collection_name}
        - Local collection: {collection_name}

    Bounding Box:
        Calculated from the combined bounds of all mesh objects in the
        collection, converted to Three.js Y-up coordinate system.
    """

    entity_type = "static"

    def matches(self, obj: bpy.types.Object) -> bool:
        """Match EMPTY objects that instance collections.

        Args:
            obj: Blender object to check.

        Returns:
            True if object is a collection instance.
        """
        if obj.type != "EMPTY":
            return False

        if obj.instance_type != "COLLECTION":
            return False

        if obj.instance_collection is None:
            return False

        return True

    def extract(self, obj: bpy.types.Object) -> Instance:
        """Extract collection instance data.

        Args:
            obj: Blender EMPTY object with collection instance.

        Returns:
            Instance dataclass with extracted data.
        """
        transform = get_object_transform(obj)

        # Determine entity type from property or default
        entity_type = self.entity_type
        if hasattr(obj, "trivesta"):
            entity_type = obj.trivesta.entity_type

        # Generate asset key from collection + library
        asset_id = self._generate_asset_key(obj)

        # Calculate bounding box from collection contents
        bounding_box = self._calculate_collection_bounding_box(obj)

        # Get base custom properties
        custom_properties = get_custom_properties(obj)

        # Serialize dialog/script_id for NPC and Interactive entities
        if hasattr(obj, "trivesta"):
            settings = obj.trivesta

            # Serialize dialog lines for NPC entities
            if settings.entity_type == "npc" and len(settings.dialog_lines) > 0:
                dialog_data = []
                for line in settings.dialog_lines:
                    dialog_data.append(
                        {
                            "speaker": line.speaker,
                            "text": line.text,
                        }
                    )
                custom_properties["dialog"] = dialog_data

            # Serialize script_id for Interactive entities
            if settings.entity_type == "interactive" and settings.script_id:
                custom_properties["script_id"] = settings.script_id

        return Instance(
            id=self._generate_instance_id(obj),
            name=obj.name,
            asset_id=asset_id,
            entity_type=entity_type,
            position=tuple(transform["position"]),
            rotation=tuple(transform["rotation"]),
            scale=tuple(transform["scale"]),
            bounding_box=bounding_box,
            collection_path=self._get_collection_path(obj),
            custom_properties=custom_properties,
        )

    def _generate_asset_key(self, obj: bpy.types.Object) -> str | None:
        """Generate asset key from collection and library source.

        Overrides base class to handle collection-specific asset key generation.

        For linked collections: {library_name}_{collection_name}
        For local collections: {collection_name}

        Args:
            obj: EMPTY object with instance_collection.

        Returns:
            Sanitized asset key, or None if no collection.
        """
        coll = obj.instance_collection
        if coll is None:
            return None

        coll_name = coll.name

        # Check if collection is from external library
        if coll.library:
            filepath = coll.library.filepath
            basename = os.path.basename(filepath) if filepath else ""
            lib_name = os.path.splitext(basename)[0] if basename else ""
            # Fallback to collection name only if library path is empty/invalid
            if lib_name:
                key = f"{lib_name}_{coll_name}"
            else:
                key = coll_name
        else:
            key = coll_name

        return sanitize_name(key)

    def _calculate_collection_bounding_box(self, obj: bpy.types.Object) -> BoundingBox:
        """Calculate combined bounding box from all objects in collection.

        Note: Uses collection.all_objects which includes objects from nested
        collections. Bounding box encompasses the entire collection hierarchy.

        Args:
            obj: EMPTY object with instance_collection.

        Returns:
            BoundingBox dict with min/max/radius in Three.js coordinates.
        """
        from mathutils import Vector

        coll = obj.instance_collection
        if coll is None:
            return {"min": [0, 0, 0], "max": [0, 0, 0], "radius": 0.0}

        # Collect all bounding box corners from mesh objects
        all_corners: list[Vector] = []
        for coll_obj in coll.all_objects:
            if coll_obj.type != "MESH" or coll_obj.data is None:
                continue

            # Get world-space bounding box corners relative to collection
            for corner in coll_obj.bound_box:
                world_corner = coll_obj.matrix_world @ Vector(corner)
                all_corners.append(world_corner)

        if not all_corners:
            return {"min": [0, 0, 0], "max": [0, 0, 0], "radius": 0.0}

        # Convert to Three.js coordinates (Y-up)
        # Blender: X right, Y forward, Z up
        # Three.js: X right, Y up, Z back
        # Conversion: x -> x, z -> y, -y -> z
        min_corner = [
            min(c.x for c in all_corners),
            min(c.z for c in all_corners),  # Blender Z -> Three.js Y
            min(-c.y for c in all_corners),  # Blender -Y -> Three.js Z
        ]
        max_corner = [
            max(c.x for c in all_corners),
            max(c.z for c in all_corners),
            max(-c.y for c in all_corners),
        ]

        # Calculate radius as distance from center to corner
        center = [
            (min_corner[0] + max_corner[0]) / 2,
            (min_corner[1] + max_corner[1]) / 2,
            (min_corner[2] + max_corner[2]) / 2,
        ]
        dx = max_corner[0] - center[0]
        dy = max_corner[1] - center[1]
        dz = max_corner[2] - center[2]
        radius = math.sqrt(dx * dx + dy * dy + dz * dz)

        return {"min": min_corner, "max": max_corner, "radius": radius}
