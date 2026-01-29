"""Base entity extractor interface.

This module defines the abstract base class for entity extractors.
Each extractor is responsible for detecting if an object matches its type
and extracting relevant data from matching objects.

Design Pattern: Strategy
    Each extractor is a strategy for handling a specific entity type.
    Extractors are checked in order; first match wins.

Manual Test Checklist (Blender Python Console):
-----------------------------------------------
1. Test abstract methods are enforced:
   >>> from blender_extension.entities.base import EntityExtractor
   >>> class BadExtractor(EntityExtractor):
   ...     pass
   >>> ext = BadExtractor()  # Should raise TypeError

2. Test helper methods work:
   >>> from blender_extension.entities.static import StaticExtractor
   >>> import bpy
   >>> ext = StaticExtractor()
   >>> obj = bpy.context.object
   >>> print(ext._generate_instance_id(obj))  # Should print ID
   >>> print(ext._get_collection_path(obj))   # Should print path list
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import bpy

from blender_extension.core.data import Instance
from blender_extension.utils.collections import get_collection_path
from blender_extension.utils.naming import generate_asset_key, generate_instance_id


class EntityExtractor(ABC):
    """Abstract base class for entity extractors.

    Each extractor is responsible for:
    1. Detecting if an object matches its type (matches())
    2. Extracting relevant data from matching objects (extract())

    Subclasses must implement:
        - matches(obj: bpy.types.Object) -> bool
        - extract(obj: bpy.types.Object) -> Instance

    Attributes:
        entity_type: String identifier for this entity type.
                     Used for categorization in export data.
    """

    entity_type: str = "unknown"

    @abstractmethod
    def matches(self, obj: bpy.types.Object) -> bool:
        """Check if this extractor handles the given object.

        This method is called during object iteration to determine
        which extractor should handle each object. Extractors are
        checked in priority order; first match wins.

        Args:
            obj: Blender object to check.

        Returns:
            True if this extractor should handle the object.
        """
        pass

    @abstractmethod
    def extract(self, obj: bpy.types.Object) -> Instance:
        """Extract instance data from the object.

        Called only for objects that matched this extractor.
        Must return a fully populated Instance dataclass.

        Args:
            obj: Blender object to extract from.

        Returns:
            Instance dataclass with extracted data.
        """
        pass

    def _get_collection_path(self, obj: bpy.types.Object) -> list[str]:
        """Get the collection hierarchy path for an object.

        Delegates to utils.collections.get_collection_path for
        consistent path generation across the codebase.

        Args:
            obj: Blender object to find path for.

        Returns:
            List of collection names from root to direct parent.
            Empty list if object is not in any collection.
        """
        return get_collection_path(obj)

    def _generate_instance_id(self, obj: bpy.types.Object) -> str:
        """Generate a unique instance ID for an object.

        Delegates to utils.naming.generate_instance_id for
        consistent ID generation across the codebase.

        Args:
            obj: Blender object to generate ID for.

        Returns:
            Unique instance ID string.
        """
        return generate_instance_id(obj)

    def _generate_asset_key(self, obj: bpy.types.Object) -> str | None:
        """Generate asset key from library source or mesh name.

        Returns None for local objects without library source,
        indicating they should not be treated as instanced assets.

        Args:
            obj: Blender object to generate key for.

        Returns:
            Asset key string, or None for local/terrain objects.
        """
        from blender_extension.utils.transforms import get_library_source

        source = get_library_source(obj)
        if source:
            return generate_asset_key(obj)
        return None
