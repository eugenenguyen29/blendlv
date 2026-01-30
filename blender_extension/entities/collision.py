"""Collision mesh entity extractor.

This module provides the CollisionExtractor class for extracting data from
collision meshes. Collision meshes are simplified geometry used for physics
and collision detection, typically invisible to players.
"""

from __future__ import annotations

import bpy

from blender_extension.core.data import Instance
from blender_extension.entities.base import EntityExtractor
from blender_extension.utils.transforms import (
    get_bounding_box,
    get_custom_properties,
    get_object_transform,
)


class CollisionExtractor(EntityExtractor):
    """Extractor for collision meshes.

    Collision meshes are identified by various conventions:
    - Property marker
    - Name suffix
    - Collection membership

    Matching logic (any of these):
        1. Object property: trivesta.is_collision = True
        2. Object name ends with "_collision" (case-insensitive)
        3. Object is in a collection named "Collision" (case-insensitive)

    Additional Data:
        If the object is within an "Island_*" collection hierarchy,
        the island_id is stored in custom_properties for linking
        collision meshes to their parent islands.
    """

    entity_type = "collision"

    def matches(self, obj: bpy.types.Object) -> bool:
        """Check if object is a collision mesh.

        Args:
            obj: Blender object to check.

        Returns:
            True if object matches collision detection criteria.
        """
        if obj.type != "MESH":
            return False

        # Explicit collision marking via property
        if hasattr(obj, "trivesta") and obj.trivesta.is_collision:
            return True

        # Name convention: *_collision
        if obj.name.lower().endswith("_collision"):
            return True

        # Collection convention: objects in "Collision" collection
        for collection in obj.users_collection:
            if collection.name.lower() == "collision":
                return True

        return False

    def extract(self, obj: bpy.types.Object) -> Instance:
        """Extract collision mesh data.

        Collision meshes have no asset_id because they are typically
        unique to their location. If the object is within an Island_*
        collection, the island_id is stored for reference.

        Args:
            obj: Blender mesh object to extract from.

        Returns:
            Instance dataclass with extracted data.
        """
        transform = get_object_transform(obj)

        # Determine parent island from collection path
        collection_path = self._get_collection_path(obj)
        island_id = self._find_island_id(collection_path)

        # Get existing custom properties and merge with island_id if found
        custom_props = get_custom_properties(obj)
        if island_id:
            custom_props["island_id"] = island_id

        return Instance(
            id=self._generate_instance_id(obj),
            name=obj.name,
            asset_id=None,  # Collision meshes are not instanced
            entity_type=self.entity_type,
            position=tuple(transform["position"]),
            rotation=tuple(transform["rotation"]),
            scale=tuple(transform["scale"]),
            bounding_box=get_bounding_box(obj),
            collection_path=collection_path,
            custom_properties=custom_props,
        )

    def _find_island_id(self, collection_path: list[str]) -> str | None:
        """Find island ID from collection path.

        Searches the collection path for a collection starting with
        "Island_" and returns a sanitized ID.

        Args:
            collection_path: List of collection names from root to object.

        Returns:
            Sanitized island ID, or None if not in an island.
        """
        for part in collection_path:
            if part.lower().startswith("island_"):
                return part.lower().replace(" ", "_")
        return None
