"""Core module - domain models, properties, and constants.

This module provides the foundational infrastructure for the Trivesta Level
extension. It contains:

- Constants: Entity types, versions, and default values
- Properties: Blender PropertyGroups for scene and object settings
- Data: Dataclasses for export data structures
- Registry: Class registration utilities

Usage:
    from blender_extension.core import (
        ENTITY_TYPES,
        MANIFEST_VERSION,
        TrivestaSceneSettings,
        Instance,
        ExportData,
    )
"""

from .constants import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_EXPORT_PATH,
    ENTITY_TYPES,
    EXPORT_MODE_COMBINED,
    EXPORT_MODE_SEPARATED,
    MANIFEST_VERSION,
    MANIFEST_VERSION_LEGACY,
)
from .data import (
    AssetDefinition,
    BoundingBox,
    CollectionNode,
    CollectionNodeDict,
    ExportData,
    Instance,
    Island,
    WorldMap,
)
from .properties import (
    TrivestaObjectSettings,
    TrivestaSceneSettings,
    register_properties,
    unregister_properties,
)
from .registry import collect_classes

__all__ = [
    # Constants
    "ENTITY_TYPES",
    "MANIFEST_VERSION",
    "MANIFEST_VERSION_LEGACY",
    "DEFAULT_EXPORT_PATH",
    "DEFAULT_CHUNK_SIZE",
    "EXPORT_MODE_COMBINED",
    "EXPORT_MODE_SEPARATED",
    # Properties
    "TrivestaSceneSettings",
    "TrivestaObjectSettings",
    "register_properties",
    "unregister_properties",
    # Registry
    "collect_classes",
    # Data models
    "BoundingBox",
    "CollectionNodeDict",
    "Instance",
    "AssetDefinition",
    "CollectionNode",
    "Island",
    "WorldMap",
    "ExportData",
]
